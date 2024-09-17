"""
This file is declare a lib manage temp directories and file for background processing

"""
import os.path
import sys
import threading
import time

from icecream import ic
import hashlib


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
class ExtractTextFileService:
    """
    This class is used to manage temp directories and file for background processing
    """
    file_util_service = cy_kit.singleton(FileUtilService)
    search_engine = cy_kit.singleton(SearchEngine)
    def __init__(self):
        self.__file_storage_path__ = config.file_storage_path
        self.__temp_dir_name__ = "__tmp_dir__"
        self.__decrypt_dir_name__= "__decrypt_dir__"
        self.__temp_dir__ = os.path.join(self.__file_storage_path__,self.__temp_dir_name__).replace('/',os.sep)
        self.__decrypt_dir__ = os.path.join(self.__temp_dir__,self.__decrypt_dir_name__).replace('/',os.sep)
        self.__producer__: Consumer = None
        self.__consumer_es: Consumer = None
        os.makedirs(self.__temp_dir__,exist_ok=True)
        os.makedirs(self.__decrypt_dir__, exist_ok=True)

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


    def decrypt_file(self, encrypted_file_path:str)->str|None:
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
                    df.write(data)
                    data = fs.read(256 * 1024)
        return decrypted_file_path
    def get_and_decrypted_file(self,app_name,upload_id:str)->str|None:
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
        parsed_data = tika_parse.from_file(file_path, serverEndpoint=config.tika_server)

        content = parsed_data.get("content","") or ""
        content = content.lstrip('\n').rstrip('\n').replace('\n',' ').replace('\r',' ').replace('\t',' ')
        while "  " in content:
            content = content.replace("  "," ")
        content = content.rstrip(' ').lstrip(' ')
        return content

    def producer_office_content(self, app_name:str, msg:str):
        if not self.__producer__:
            self.__producer__= Consumer(msg)
        agg = Repository.files.app(app_name).context.aggregate().match(
            Repository.files.fields.Status==1
        ).match(
            { Repository.files.fields.FileExt.__name__ :{"$in":config.ext_office_file}}
        ).match(
            (Repository.files.fields.HasORCContent==None)|(Repository.files.fields.HasORCContent==False)
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

    def consumer_office_content(self,msg):
        if not self.__producer__:
            self.__producer__= Consumer(msg)
        rb_msg = self.__producer__.get_msg(delete_after_get=False)
        if not  rb_msg:
            time.sleep(0.2)
            return
        data = rb_msg.data
        app_name = rb_msg.app_name
        file_path:str = data.get(Repository.files.fields.MainFileId.__name__) or ""
        if not file_path.startswith("local://"):
            self.__producer__.channel.basic_ack(msg.method.delivery_tag)
            self.update_upload_office_content(app_name=app_name, upload_id=data.get("_id"),msg=msg)
            return

        file_path = os.path.join(self.__file_storage_path__,file_path.split("://")[1])
        if not  os.path.isfile(file_path):
            self.__producer__.channel.basic_ack(msg.method.delivery_tag)
            self.update_upload_office_content(app_name=app_name, upload_id=data.get("_id"),msg=msg)
            return
        process_file = self.decrypt_file(encrypted_file_path=file_path)
        content = self.extract_text_by_using_tika_server(file_path=process_file)
        dir_of_server_file = pathlib.Path(process_file).parent.__str__()
        content_of_server_file_es = os.path.join(dir_of_server_file,pathlib.Path(process_file).stem+".content.txt")
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
        self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
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
    def consumer_save_es(self, msg):
        if self.__consumer_es  is None:
            self.__consumer_es =  Consumer(f"{msg}_es_update")
        rb_msg = self.__consumer_es.get_msg(delete_after_get=False)
        if not rb_msg:
            return
        content_file = rb_msg.data.get("content-file") or ""
        app_name = rb_msg.app_name
        upload_id = rb_msg.data.get("_id")
        if not os.path.isfile(content_file):
            self.__consumer_es.channel.basic_ack(rb_msg.method.delivery_tag)
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
            self.__consumer_es.channel.basic_ack(rb_msg.method.delivery_tag)
            return
        content = None
        with open(content_file,"rb") as fs:
            content = fs.read().decode()
            ic(content[0:20])
            self.do_update_es(
                client=self.client,
                app_name = app_name,
                upload_id = upload_id,
                data_item = upload,
                content = content
            )
            self.__consumer_es.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_office_content(
                app_name=app_name,
                upload_id=upload_id,
                msg=msg
            )


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


    def consumer_save_es_loop_task(self, msg)->threading.Thread:
        def running():
            while True:
                time.sleep(0.3)
                self.consumer_save_es(msg=msg)
        return threading.Thread(target=running)


if __name__ == "__main__":
    app_name = "developer"
    msg= "office-content"
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


