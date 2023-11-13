import os.path
import pathlib
import shutil
import threading
import typing
from asynchat import simple_producer

import cy_kit
from cyx.common.base import T
from typing import List
from cy_plugins.file_storage_hybrid import HybridFileStorage
from cy_plugins.files_storage_hybrid_reader import HybridReader
from cyx.common import config
from cyx.common.base import DbConnect
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.common.file_storage_mongodb import MongoDbFileService, MongoDbFileStorage
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister
from enum import Enum

class StorageTypeEnum(Enum):
  MONGO_DB = "MONGO_DB"
  LOCAL = "LOCAL"

class StorageTypeInfo:
    storage_type: StorageTypeEnum
    local_path: str


class FileStorageService:
    def __init__(self,
                 cacher=cy_kit.singleton(MemcacheServices),
                 db_connect=cy_kit.singleton(DbConnect),
                 file_services= cy_kit.singleton(FileServices)
                 ):
        self.cacher = cacher
        self.db_connect = db_connect
        self.mongo_file_service = MongoDbFileService()
        self.file_services = file_services
        if not hasattr(config, "file_storage_path"):
            raise Exception(f"file_storage_path was not found in config")
        self.file_storage_path = config.file_storage_path
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        if not isinstance(self.file_storage_path, str):
            raise Exception(f"file_storage_path in config must be string")
        if self.file_storage_path.startswith("./"):
            self.file_storage_path = os.path.abspath(
                os.path.join(
                    self.working_dir,
                    self.file_storage_path[2:]
                )
            )
        if not os.path.isdir(self.file_storage_path):
            os.makedirs(self.file_storage_path, exist_ok=True)
        if not os.path.isdir(self.file_storage_path):
            raise Exception(f"{self.file_storage_path} was not found")

    async def create_async(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
                     size) -> HybridFileStorage:
        """
        somehow to implement thy source here ...
        """
        return  self.create(
            app_name=app_name,
            rel_file_path=rel_file_path,
            content_type=content_type,
            chunk_size=chunk_size,
            size=size
        )



    def get_file_async(self, app_name: str, file_id):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_info_by_id(self, app_name, id):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def create(self, app_name: str,
               rel_file_path: typing.Optional[str],
               content_type: typing.Optional[str],
               chunk_size: typing.Optional[int],
               size: typing.Optional[int]) -> HybridFileStorage:
        """
        somehow to implement thy source here ...
        """
        return HybridFileStorage(
            file_storage_path=self.file_storage_path,
            app_name = app_name,
            rel_file_path = rel_file_path,
            content_type=content_type,
            chunk_size=chunk_size,
            size=size,
            cacher= self.cacher,
            file_services = self.file_services


        )

    def store_file(self, app_name: str, source_file: str, rel_file_store_path: str) -> typing.Union[HybridFileStorage,MongoDbFileStorage]:
        """
        somehow to implement thy source here ...
        """
        id = rel_file_store_path.split('/')[1]
        if not self.__is_uuid__(id):
            return self.mongo_file_service.store_file(
                app_name,
                source_file=source_file,
                rel_file_store_path=rel_file_store_path
            )
        else:
            upload = self.file_services.get_upload_register_with_cache(
                app_name = app_name,
                upload_id= id
            )
            doc_type="unknown"
            if upload.get("FileExt"):
                doc_type=upload["FileExt"][0:3]
            register_on = upload.RegisterOn
            filename = os.path.split(source_file)[1]
            locate_path = os.path.join(
                app_name,
                f"{register_on.year}",
                f"{register_on.month:02}",
                f"{register_on.day:02}",
                doc_type,
                id,
                filename
            )
            full_path = os.path.join(self.file_storage_path, locate_path)

            full_dir = pathlib.Path(full_path).parent.__str__()

            if not os.path.isdir(full_dir):
                os.makedirs(full_dir,exist_ok=True)
            try:
                shutil.move(source_file, full_dir)
            except shutil.Error  as e:
                if e.args[0].endswith(" already exists"):
                    pass
                else:
                    raise e
        hybrid_rel_file_store_path = os.path.join(pathlib.Path(rel_file_store_path).parent.__str__(),pathlib.Path(rel_file_store_path).stem)
        ret = HybridFileStorage(
            file_storage_path=self.file_storage_path,
            app_name=app_name,
            rel_file_path=rel_file_store_path,
            content_type=None,
            chunk_size=0,
            size=0,
            cacher=self.cacher,
            file_services=self.file_services

        )
        ret.id = locate_path
        ret.full_id = locate_path
        return ret

    def db_name(self, app_name: str):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def copy_by_id(self, app_name: str, file_id_to_copy: str, rel_file_path_to: str,
                   run_in_thread: bool) -> HybridFileStorage:
        """
                Copy file from id file and return new copy if successful
                :param app_name:
                :param file_id_to_copy:
                :param run_in_thread:
                :return:
                        """
        if not file_id_to_copy.startswith("local://"):
            return self.mongo_file_service.copy_by_id(
                app_name=app_name,
                file_id_to_copy=file_id_to_copy,
                rel_file_path_to=rel_file_path_to,
                run_in_thread=run_in_thread
            )
        else:
            source = self.get_file_by_id(
                app_name=app_name,
                id=file_id_to_copy
            )
            if not source:
                return None
            dest = self.create(
                app_name=app_name,
                rel_file_path=rel_file_path_to,
                chunk_size=0,
                size=0,
                content_type=None
            )

            @cy_kit.thread_makeup()
            def process(s: HybridFileStorage, d: HybridFileStorage):
                # if os.path.isfile(s.full_path):
                #     full_des_dir = pathlib.Path(d.full_path).parent.__str__()
                #     os.makedirs(full_des_dir,exist_ok=True)
                source_dir = pathlib.Path(s.full_path).parent.__str__()
                dest_dir = pathlib.Path(d.full_path).parent.__str__()
                shutil.copytree(source_dir,dest_dir, dirs_exist_ok=True)


            if run_in_thread:
                process(source, dest).start()
            else:
                process(source, dest).join()
            return dest

    def copy(self, app_name: str, rel_file_path_from: str, rel_file_path_to, run_in_thread: bool) -> typing.Union[None,MongoDbFileStorage]:
        """
                Copy file
                :param rel_file_path_to:
                :param rel_file_path_from:
                :param app_name:
                :param run_in_thread:True copy process will run in thread
                :return:
                        """
        if not rel_file_path_from.startswith("local://"):
            return self.mongo_file_service.copy(
                app_name=app_name,
                rel_file_path_to=rel_file_path_to,
                rel_file_path_from=rel_file_path_from,
                run_in_thread=run_in_thread
            )

    def db(self, app_name: str):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def delete_files(self, app_name, files: List[str], run_in_thread: bool):
        for x in files or []:
            if x is None:
                continue
            if self.__is_uuid__(x) or not x.startswith("local://"):
                self.mongo_file_service.delete_files_by_id(app_name=app_name,ids=[x],run_in_thread=run_in_thread)
            elif x.startswith("local://"):
                rel_path = x[len("local://"):]
                delete_dir_path =pathlib.Path(os.path.join(self.file_storage_path,rel_path)).parent.__str__()
                if os.path.isdir(delete_dir_path):
                    th_os_delete = threading.Thread(target= shutil.rmtree,args=(delete_dir_path,))
                    try:
                        if run_in_thread:
                            th_os_delete.start()
                        else:
                            th_os_delete.run()
                    except:
                        pass



        """
        somehow to implement thy source here ...
        """
    def delete_files_by_id(self, app_name: str, ids: List, run_in_thread: bool):
        """
        somehow to implement thy source here ...
        """
        for x in ids or []:
            if x is None:
                continue
            if self.__is_uuid__(x) or not x.startswith("local://"):
                self.mongo_file_service.delete_files_by_id(app_name=app_name, ids=[x], run_in_thread=run_in_thread)
            elif x.startswith("local://"):
                rel_path = x[len("local://"):]
                delete_dir_path = pathlib.Path(os.path.join(self.file_storage_path, rel_path)).parent.__str__()
                if os.path.isdir(delete_dir_path):
                    th_os_delete = threading.Thread(target= shutil.rmtree, args=(delete_dir_path,))
                    try:
                        if run_in_thread:
                            th_os_delete.start()
                        else:
                            th_os_delete.run()
                    except:
                        pass

    async def get_file_by_name_async(self, app_name, rel_file_path: str) -> HybridFileStorage:
        """
        somehow to implement thy source here ...
        """
        return self.get_file_by_name(app_name=app_name,rel_file_path=rel_file_path)


    def get_file_by_id(self, app_name: str, id: str) ->typing.Union[HybridFileStorage,MongoDbFileStorage]:
        # storage_info = self.__get_storage_type_by_app_and_id__(app_name,id)
        if isinstance(id,str) and id.startswith("local://"):
            ret = HybridFileStorage(
                file_storage_path=self.file_storage_path,
                app_name=app_name,
                rel_file_path=id,
                content_type=None,
                chunk_size=0,
                size=0,
                file_services=self.file_services,
                cacher= self.cacher,

            )
            return ret
        else:
            return self.mongo_file_service.get_file_by_id(app_name, id)

    def expr(self, cls: T) -> T:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    async def get_file_by_id_async(self, app_name: str, id: str) ->typing.Union[HybridFileStorage,MongoDbFileStorage]:
        return self.get_file_by_id(app_name,id)

    def get_reader_of_file(self, app_name: str, from_chunk, id) -> HybridReader:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_name(self, app_name, rel_file_path: str) ->typing.Union[HybridFileStorage,MongoDbFileStorage]:
        storage_info = self.__get_storage_type_by_app_and_rel_path__(app_name,rel_file_path)
        if storage_info is None:
            raise FileNotFoundError(f"{app_name}/{rel_file_path} is no longer")
        if storage_info.storage_type == StorageTypeEnum.MONGO_DB:
            return self.mongo_file_service.get_file_by_name(app_name, rel_file_path)
        else:
            return HybridFileStorage(
                app_name=app_name,
                rel_file_path = rel_file_path,
                content_type = None,
                chunk_size =0,
                size =0,
                file_services = self.file_services,
                cacher =self.cacher,
                file_storage_path=self.file_storage_path


            )

    def __is_uuid__(self,str_value):
        import re
        regex = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        return regex.match(str_value) is not None
    def __get_storage_type_by_app_and_rel_path__(self, app_name, rel_file_path)->StorageTypeInfo:
        key = f"{app_name}/{rel_file_path}".replace(" ","___")
        ret = self.cacher.get_object(key,StorageTypeInfo)
        if ret is None:
            id = rel_file_path.split('/')[0]
            if not self.__is_uuid__(id):
                id = rel_file_path.split('/')[1]
            upload = self.file_services.get_upload_register(app_name, id)
            if upload is not None:
                if upload.StoragePath is None:
                    ret = StorageTypeInfo()
                    ret.storage_type= StorageTypeEnum.MONGO_DB
                    self.cacher.set_object(key,ret)
                elif isinstance(upload.StoragePath,str) and upload.StoragePath.startswith("local://"):
                    ret = StorageTypeInfo()
                    ret.storage_type = StorageTypeEnum.LOCAL
                    ret.local_path = upload.StoragePath[len("local://"):]
                    self.cacher.set_object(key, ret)
        return ret

    def __get_storage_type_by_app_and_id__(self, app_name, main_id_file):
        key = f"{app_name}/{id}".replace(" ", "___")
        ret = self.cacher.get_object(key, StorageTypeInfo)
        if ret is None:

            upload = self.file_services.get_find_upload_register_by_link_file_id(app_name, main_id_file)
            if upload is not None:
                if upload.StoragePath is None:
                    ret = StorageTypeInfo()
                    ret.storage_type = StorageTypeEnum.MONGO_DB
                    self.cacher.set_object(key, ret)
        return ret



