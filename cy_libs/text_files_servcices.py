"""
This file is declare a lib manage temp directories and file for background processing

"""
import os.path
import sys
import threading
import time
import traceback

from icecream import ic
import hashlib

import cy_docs
from cyx.common import config
import pathlib
__working_dir__ =pathlib.Path(__file__).parent.parent.__str__()



sys.path.append(__working_dir__)
from cyx.file_utils_services import FileUtilService
from cy_file_cryptor import wrappers, context
from cyx.repository import Repository
context.set_server_cache(config.cache_server)
import cy_kit
from tika import parser as tika_parse
from cyx.rabbit_utils import Consumer
from elasticsearch import Elasticsearch
from cy_xdoc.services.search_engine import SearchEngine
import elasticsearch.exceptions
from cyx.malloc_services import MallocService
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
from retry import retry
import requests.exceptions
import typing
import unicodedata
from PyPDF2 import PdfReader
import PyPDF2.errors
import cy_es.cy_es_manager
class ExtractTextFileService:
    """
    This class is used to manage temp directories and file for background processing
    """
    file_util_service = cy_kit.singleton(FileUtilService)
    search_engine = cy_kit.singleton(SearchEngine)
    malloc_service = cy_kit.singleton(MallocService)
    logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)
    def __init__(self):
        self.__file_storage_path__ = config.file_storage_path
        msg = config.get("msg_process") or "v-002"
        self.__temp_dir_name__ = f"__tmp_dir_office__{msg}"
        self.__temp_dir_result_name__ = f"__tmp_dir_office_result__{msg}"
        self.__temp_dir_result__ = os.path.join(config.file_storage_path,self.__temp_dir_result_name__)
        self.__decrypt_dir_name__= "__decrypt_dir__"
        self.__temp_dir__ = os.path.join(self.__file_storage_path__,self.__temp_dir_name__).replace('/',os.sep)
        self.__decrypt_dir__ = os.path.join(self.__temp_dir__,self.__decrypt_dir_name__).replace('/',os.sep)

        self.__producer__: Consumer = None
        self.__consumer_es: Consumer = None
        os.makedirs(self.__temp_dir__,exist_ok=True)
        os.makedirs(self.__decrypt_dir__, exist_ok=True)
        os.makedirs(self.__temp_dir_result__, exist_ok=True)
        self.client: Elasticsearch = self.search_engine.client

    @property
    def file_storage_path(self)->str:
        """
        This property is used to get the file storage path
        """
        return self.__file_storage_path__

    @property
    def temp_dir(self)->str:
        """
        Gte temp directories
        @return:
        """
        return self.__temp_dir__

    @property
    def decrypt_dir(self):
        return self.__decrypt_dir__


    def decrypt_file(self, encrypted_file_path:str)->typing.Union[str,None]:
        """
        decrypted file in to decrypt_dir, filename is hash256 of filepath
        @param encrypted_file_path:
        @return:
        """
        if not os.path.isfile(encrypted_file_path):
            return None
        decrypted_file_name:str = hashlib.sha256(encrypted_file_path.encode()).hexdigest()
        decrypted_file_path:str = os.path.join(self.decrypt_dir,decrypted_file_name)
        with open(encrypted_file_path,"rb") as fs:
            with open(decrypted_file_path,"wb") as df:
                data = fs.read(256*1024)
                while data:
                    if isinstance(data,str):
                        df.write(data.encode())
                    else:
                        df.write(data)
                    data = fs.read(256 * 1024)
        return decrypted_file_path
    def get_and_decrypted_file(self,app_name,upload_id:str)->typing.Union[str,None]:
        """
        This method get physical file path and decrypt to new file
        return decrypted file
        @param app_name:
        @param upload_id:
        @return:
        """
        file_path = self.file_util_service.get_physical_path(app_name=app_name,
                                                            upload_id=upload_id)
        if not file_path or not os.path.isfile(file_path):
            return None
        return self.decrypt_file(encrypted_file_path=file_path)
    def extract_text_by_using_tika_server(self, file_path:str):
        @retry(exceptions=(requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError),delay=15,tries=10)
        def runing():

            parsed_data = tika_parse.from_file(file_path,
                                               serverEndpoint=config.tika_server,
                                               xmlContent = False,
                                               requestOptions = {'timeout': 5000})

            content = parsed_data.get("content","") or ""
            content = content.lstrip('\n').rstrip('\n').replace('\n',' ').replace('\r',' ').replace('\t',' ')
            while "  " in content:
                content = content.replace("  "," ")
            content = content.rstrip(' ').lstrip(' ')
            return content
        return runing()


    def producer_office_content(self, app_name:str, msg:str):
        if not self.__producer__:
            self.__producer__= Consumer(msg)
        agg = Repository.files.app(app_name).context.aggregate().match(
            Repository.files.fields.Status==1
        ).match(
            { Repository.files.fields.FileExt.__name__ :{"$in":config.ext_office_file}}
        ).match(
            Repository.files.fields.MsgOfficeContentReRaise!=msg

        ).sort(
            Repository.files.fields.RegisterOn.desc()
        ).limit(1)
        for item in agg:
            self.__producer__.raise_message(
                app_name=app_name,
                data=item.to_json_convertable(),
                msg_type=msg
            )
            ic(f"raise msg={msg} in app={app_name}")
            ic(item.to_json_convertable())
            self.update_upload_office_content(app_name=app_name, upload_id=item.id, msg=msg)
    def read_text_from_file(self,pdf_file)->str:
        contents = []
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            contents.append(page.extract_text())
        del reader
        return " ".join(contents)

    def consumer_office_content(self, msg):
        try:
            return self.consumer_office_content_no_exception(msg)
        except:
            self.logs_to_mongo_db_service.log(
                error_content=traceback.format_exc(),
                url=msg.data.get(Repository.files.fields.MainFileId.__name__) or ""
            )

    def consumer_office_content_no_exception(self,msg):
        """
        Consume msg office content and generate new msg with tail fix is _es_update
        The message data also have new key is 'content-file' with value is value of text file (real and purely content of oofice file)
        Example:
        rabbitmq msg is 'v-002'
        new rabbit msg is 'v-002_es_update'
        @param msg:
        @return:
        """
        if not self.__producer__:
            self.__producer__= Consumer(msg)
        rb_msg = self.__producer__.get_msg()
        if not  rb_msg:
            time.sleep(0.2)
            return
        data = rb_msg.data
        app_name = rb_msg.app_name
        file_path:str = data.get(Repository.files.fields.MainFileId.__name__) or ""
        if not file_path.startswith("local://"):
            self.__producer__.delete_msg(rb_msg)
            self.update_upload_office_content(app_name=app_name, upload_id=data.get("_id"),msg=msg)
            return

        file_path = os.path.join(self.__file_storage_path__,file_path.split("://")[1])
        if not  os.path.isfile(file_path):
            self.__producer__.delete_msg(rb_msg)
            self.update_upload_office_content(app_name=app_name, upload_id=data.get("_id"),msg=msg)
            return
        process_file = self.decrypt_file(encrypted_file_path=file_path)
        if data[Repository.files.fields.FileExt.__name__].lower()=="pdf":
            try:
                content = self.read_text_from_file(pdf_file=process_file)
            except:
                content = self.extract_text_by_using_tika_server(file_path=process_file)
        else:
            content = self.extract_text_by_using_tika_server(file_path=process_file)

        content_file_name = f"{hashlib.sha256(file_path.encode()).hexdigest()}.txt"
        content_of_server_file_es = os.path.join(self.__temp_dir_result__,content_file_name)
        with open(content_of_server_file_es,"wb") as fs:
            fs.write(content.encode())
        data["content-file"] = content_of_server_file_es
        self.__producer__.raise_message(
            app_name=app_name,
            data = data,
            msg_type= f"{msg}_es_update"
        )
        ic(content[0:20])
        ic(data)
        self.__producer__.delete_msg(rb_msg.method)
        self.update_upload_office_content(app_name=app_name, upload_id=data.get("_id"),msg=msg)
    def update_upload_office_content(self, app_name, upload_id,msg):
        Repository.files.app(app_name).context.update(
            Repository.files.fields.id==upload_id,
            Repository.files.fields.MsgOfficeContentReRaise<<msg
        )

    def do_update_es(self,client: Elasticsearch, app_name: str,upload_id:str,data_item,content:str):

        if isinstance(content, str) and len(content) > 0:
            update_body = {
                "doc": {
                    "content": content
                }
            }
            index_name = self.search_engine.get_index(app_name)
            try:
                response = client.update(index=index_name, doc_type="_doc", id=upload_id, body=update_body)

                # Check the response
                if response.get('result') == 'updated':
                    ic(f"Document updated successfully, app={app_name},upload_id={upload_id}")
                else:
                    self.search_engine.make_index_content(
                        app_name=app_name,
                        upload_id=upload_id,
                        data_item=data_item.to_json_convertable(),
                        privileges=data_item[Repository.files.fields.Privileges],
                        content=content

                    )
            except elasticsearch.exceptions.NotFoundError:
                self.search_engine.make_index_content(
                    app_name=app_name,
                    upload_id=upload_id,
                    data_item=data_item.to_json_convertable(),
                    privileges=data_item[Repository.files.fields.Privileges],
                    content=content

                )
    def clear__accents(self, content):
        """Removes accents from Vietnamese text.

            Args:
                content (str): The Vietnamese text to process.

            Returns:
                str: The text without accents.
            """

        normalized_form = unicodedata.normalize('NFKC', content)
        decomposed_form = unicodedata.normalize('NFKD', normalized_form)
        ret = ''.join(c for c in decomposed_form if unicodedata.category(c) != 'Mn')
        ret=ret.replace("Đ","D").replace("đ","d")
        return ret
    def save_content_elastic_search(self, app_name: str,upload_id:str,data_item,content:str):

        document_id = upload_id
        app_index = self.search_engine.get_index(app_name)

        if isinstance(content, str) and len(content) > 0:
            cy_es.cy_es_manager.update_or_insert_content(
                client=self.client,
                index= app_index,
                id = document_id,
                content = content
            )

    def consumer_save_es(self, msg):
        if self.__consumer_es  is None:
            self.__consumer_es =  Consumer(f"{msg}_es_update")
        rb_msg = self.__consumer_es.get_msg()
        if not rb_msg:
            return
        content_file = rb_msg.data.get("content-file") or ""
        app_name = rb_msg.app_name
        upload_id = rb_msg.data.get("_id")
        if not os.path.isfile(content_file):
            self.__consumer_es.delete_msg(rb_msg)
            self.update_upload_office_content(
                app_name= app_name,
                upload_id = upload_id,
                msg = msg
            )
            return

        #veryfy upload will be delete
        upload = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.id== upload_id
        )
        if not upload:
            self.__consumer_es.delete_msg(rb_msg)
            return
        content = None
        with open(content_file,"rb") as fs:
            content = fs.read().decode()
            content = content.replace('\n',' ').replace('\r',' ').replace('\t',' ')
            content = content.rstrip(' ').lstrip(' ')
            while '  ' in content:
                content = content.replace('  ',' ')
            ic(content[0:20])
            try:
                self.save_content_elastic_search(
                    app_name=app_name,
                    upload_id = upload_id,
                    data_item=None,
                    content=content
                )
                ic(f"update content to {upload_id} at {app_name} is ok")
                ic(rb_msg.data.get(Repository.files.fields.MainFileId.__name__))

            except elasticsearch.exceptions.RequestError as ex:
                self.__consumer_es.delete_msg(rb_msg)
                self.logs_to_mongo_db_service.log(
                    error_content=traceback.format_exc(),
                    url= "ElasticSearch"
                )
                raise ex



    def producer_office_content_loop_task(self, app_name, msg)->threading.Thread:
        def running():
            while True:
                time.sleep(0.3)
                self.producer_office_content(app_name=app_name, msg=msg)
        return threading.Thread(target=running)

    def consumer_office_content_loop_task(self, msg)->threading.Thread:
        def running():
            while True:
                time.sleep(0.3)
                self.consumer_office_content(msg=msg)

        return threading.Thread(target=running)

#sudo yum remove kubelet

    def consumer_save_es_loop_task(self, msg)->threading.Thread:
        def running():
            while True:
                time.sleep(0.3)
                self.consumer_save_es(msg=msg)
        return threading.Thread(target=running)


    def get_app_names(self)->typing.List[str]:
        agg = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name!=config.admin_db_name
        ).match(
            Repository.apps.fields.AccessCount>0
        ).sort(
            Repository.apps.fields.AccessCount.desc()
        ).sort(
            Repository.apps.fields.RegisteredOn.desc()
        ).project(
            cy_docs.fields.app_name >> Repository.apps.fields.Name
        )
        ret = [x.app_name.lower() for x in agg]
        return ret





if __name__ == "__main__":
    app_name = "developer"
    msg= config.get("msg_re_run") or "office-content"
    svc = cy_kit.singleton(ExtractTextFileService)
    th1 = svc.producer_office_content_loop_task(app_name=app_name,msg=msg)
    th2 = svc.consumer_office_content_loop_task(msg=msg)
    th3 = svc.consumer_save_es_loop_task(msg=msg)
    th1.start()
    th2.start()
    th3.start()
    # th1.join()
    # th2.join()
    th3.join()
    print("OK")
    # agg = Repository.files.app("developer").context.aggregate().match(
    #     Repository.files.fields.FileExt=="pdf"
    # ).sort(
    #     Repository.files.fields.RegisterOn.desc()
    # ).project(
    #     cy_docs.fields.upload_id >> Repository.files.fields.id
    # ).limit(100)
    # for upload  in agg:
    #     svc = cy_kit.singleton(ExtractTextFileService)
    #     ic(svc.temp_dir)
    #     file_path = svc.get_and_decrypted_file(app_name="developer",upload_id= upload.upload_id)
    #     decrypted_file= svc.decrypt_file(encrypted_file_path=file_path)
    #     content = svc.extract_text_by_using_tika_server(file_path=decrypted_file)
    #     ic(content[:10])


