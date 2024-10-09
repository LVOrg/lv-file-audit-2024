import hashlib
import os.path
import pathlib
import sys
import time
import traceback
import typing

from icecream import ic



sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
from cyx.common import config
import cy_kit
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache(config.cache_server)
from cyx.repository import Repository

import cy_docs
import mimetypes
from cy_xdoc.services.search_engine import SearchEngine
from elasticsearch import Elasticsearch
import elasticsearch.exceptions
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
import requests
from tika import parser as tika_parse
import retry
import unicodedata
from cy_jobs.jobs.lib_list_all_files import ListAllFilesService
from cy_lib_ocr.ocr_services import OCRService
class OCRNoRabbitMQ:

    ocr_service = cy_kit.singleton(OCRService)
    ocr_service.check()
    search_engine = cy_kit.singleton(SearchEngine)
    logs = cy_kit.singleton(LogsToMongoDbService)
    list_all_files_service = cy_kit.singleton(ListAllFilesService)
    def __init__(self):
        self.__app_name = config.get("app_name") or "all"

        self.msg = config.get("msg_process") or "viet-ocr-v008"
        self.file_storage_path = config.file_storage_path
        self.file_storage_path_tmp = os.path.join(self.file_storage_path.replace('/',os.sep),f"__{type(self).__name__.lower()}__")
        self.file_storage_path_tmp_decrypt_dir = os.path.join(self.file_storage_path_tmp,"decrypt")
        os.makedirs(self.file_storage_path_tmp_decrypt_dir,exist_ok=True)
        self.client: Elasticsearch = self.search_engine.client
        self.recent = config.get("recent") is not  None
        self.filter_field = config.get("filter_field") or "ocr-pdf"

    def save_content_elastic_search(self, app_name: str,upload_id:str,content:str):
        es =self.client
        document_id = upload_id
        app_index = self.search_engine.get_index(app_name)
        @retry.retry(delay=5,tries=10)
        def save_content(_index,_id,txt_content):
            import cy_es.cy_es_manager
            cy_es.cy_es_manager.update_or_insert_content(
                client= self.client,
                index=_index,
                id=_id,
                content=txt_content
            )
        if isinstance(content, str) and len(content) > 0:
            try:
                save_content(
                    _index=app_index,
                    _id=document_id,
                    txt_content=content
                )
                ic(f"Document updated successfully. {app_index},{document_id}")
            except:
                self.logs.log(
                    error_content=traceback.format_exc(),
                    url="ElasticSearch"
                )


        else:
            ic(f"No content for. {app_index},{document_id}")

    def get_text_from_file(self, content_file):
        if not os.path.isfile(content_file):
            return None
        with open(content_file,"rb") as fs:
            return fs.read().decode()
    def do_ocr(self):
        files = self.list_all_files_service.get_files(
            file_type="pdf",
            app_name=self.__app_name,
            recent = self.recent,
            filter_field_name= self.filter_field,
            filter_value= self.msg

        )
        for file in files:
            ic(f"tenant={file.app_name},upload_id={file.upload_id}")
            decrypt_file = file.decrypt_file()
            ic(decrypt_file)
            content_file = self.ocr_service.get_content_from_pdf(decrypt_file)
            content = self.get_text_from_file(content_file)


            self.save_content_elastic_search(
                app_name=file.app_name,
                upload_id=file.upload_id,
                content = content

            )
            file.commit()
    def delete_ge_app_names(self)->typing.List[str]:

        apps = self.get_app_names() if self.__app_name == "all" else [self.__app_name]
        return apps

    def delete_get_app_names(self) -> typing.List[str]:
        agg = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name != config.admin_db_name
        ).match(
            Repository.apps.fields.AccessCount > 0
        ).sort(
            Repository.apps.fields.LatestAccess.desc()
        ).project(
            cy_docs.fields.app_name >> Repository.apps.fields.Name
        )
        ret = [x.app_name.lower() for x in agg]
        return ret
    def delete_get_latest_upload_of_app(self, app_name):
        sort_expr = Repository.files.fields.RegisterOn.asc() if config.get("early") else Repository.files.fields.RegisterOn.desc()
        pdf_mime_type, _ = mimetypes.guess_type("x.pdf")
        Repository.files.app(app_name).context.update(
            Repository.files.fields.Status > 1,
            Repository.files.fields.Status<<1,
            Repository.files.fields.MsgOCRReRaise <<"-"
        )
        agg = Repository.files.app(app_name).context.aggregate().match(
            Repository.files.fields.Status==1
        ).match(
            (Repository.files.fields.FileExt=="pdf")
        ).match(
            (Repository.files.fields.MsgOCRReRaise==None)|(Repository.files.fields.MsgOCRReRaise!=self.msg)

        ).sort(
            sort_expr
        ).limit(1)
        ic(app_name,agg)
        upload_items = list(agg)
        if len(upload_items)>0:
            return upload_items[0]
        else:
            return  None

    def delete_get_physical_file_path(self, upload_item):

        logical_file_path = upload_item[Repository.files.fields.MainFileId]
        if not logical_file_path:
            return None
        if not "://" in logical_file_path:
            return None
        rel_file_path = logical_file_path.split("://")[1]
        return os.path.join(self.file_storage_path.replace('/',os.sep),rel_file_path)





    def delete_update_status(self, app_name, upload_id, msg):
        Repository.files.app(app_name).context.update(
            Repository.files.fields.id==upload_id,
            Repository.files.fields.MsgOCRReRaise<<msg
        )

    def delete_do_ocr_by_app_name(self, app_name):

        upload_item = self.get_latest_upload_of_app(
            app_name=app_name
        )
        if upload_item is None:
            return
        try:
            physical_file_path = self.get_physical_file_path(upload_item)
            if not physical_file_path:
                self.update_status(
                    app_name=app_name,
                    upload_id=upload_item.id,
                    msg=self.msg
                )
                return
            ic(physical_file_path)
            if not os.path.isfile(physical_file_path):
                self.update_status(
                    app_name=app_name,
                    upload_id=upload_item.id,
                    msg=self.msg
                )
                return
            decrypted_file = self.decrypted_file(physical_file_path)

            ic(decrypted_file)
            content_file = self.ocr_service.get_content_from_pdf(decrypted_file)
            ic(content_file)

            content = self.get_text_from_file(content_file)
            if not content:
                self.update_status(
                    app_name=app_name,
                    upload_id=upload_item.id,
                    msg=self.msg
                )
                return
            # app_name: str,upload_id:str,data_item,content:str
            self.save_content_elastic_search(
                app_name=app_name,
                upload_id=upload_item.id,
                content=content,
                data_item=upload_item.to_json_convertable()
            )
            self.update_status(
                app_name=app_name,
                upload_id=upload_item.id,
                msg=self.msg
            )
            ic(f"update content for {upload_item.id} {upload_item[Repository.files.fields.FullFileName]} of {app_name} is successful, content is {content[0:20]}")
        except UnicodeDecodeError:
            self.update_status(
                app_name=app_name,
                upload_id=upload_item.id,
                msg=self.msg
            )
            ic(f"update content for {upload_item.id} {upload_item[Repository.files.fields.FullFileName]} of {app_name} was fail")
            print(traceback.format_exc())
        except:
            ic(f"update content for {upload_item.id} {upload_item[Repository.files.fields.FullFileName]} of {app_name} was fail")
            print(traceback.format_exc())

    def delete_decrypted_file(self, physical_file_path:str):
        file_name = hashlib.sha256(physical_file_path.encode()).hexdigest()
        decrypted_file_path = os.path.join(self.file_storage_path_tmp_decrypt_dir,f"{file_name}.pdf")
        with open(physical_file_path,"rb") as fs:
            with open(decrypted_file_path,"wb") as fw:
                fw.write(fs.read())
                return decrypted_file_path


def main():
    svc = cy_kit.single(OCRNoRabbitMQ)
    while True:
        try:
            svc.do_ocr()
            time.sleep(0.5)
        except:
            svc.logs.log(
                error_content=traceback.format_exc(),
                url=__file__
            )
            print(traceback.format_exc())
if __name__ == "__main__":
    main()
#test
# docker run -it -v $(pwd):/app docker.lacviet.vn/xdoc/paddle-viet-ocr-core:2.2 /bin/bash
# python /app/cy_jobs/jobs/task_viet_ocr.py msg_process=long-test-ocr