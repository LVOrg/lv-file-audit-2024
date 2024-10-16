"""
This lib is all about for file:
Get Upload from mongodb with cache
Get File content
"""
import math
import mimetypes
import os
import pathlib
import shutil
import threading

import traceback
import typing
import uuid
from datetime import datetime

from humanize import naturalsize

import bson.objectid

from cyx.common import config

from cyx.repository import Repository

from cy_web.cy_web_x import streaming_async

from concurrent.futures import ThreadPoolExecutor
import asyncio



MAX_WORKERS = 10
WORKERS = dict()
from cyx.file_utils_services_base import BaseUtilService
from cy_file_cryptor.wrappers import cy_open_file

class RegisterUploadException(Exception):
    def __init__(self, Code: str, Message: str):
        super().__init__(f"[{Code}]\n{Message}")
        self.Code = Code
        self.Message = Message


class FileUtilService(BaseUtilService):
    def healthz(self):

        return "OK"

    def post_msg_upload_file(self, app_name, data, upload_id):
        if data.get("FileExt") is None:
            return
        try:
            local_share_id = self.local_api_service.generate_local_share_id(app_name=app_name, upload_id=data.Id)
            data.local_share_id = local_share_id

            self.extract_content_service.save_search_engine(
                data=data,
                app_name=app_name
            )
        except Exception as e:
            traceback_string = traceback.format_exc()
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == upload_id,
                Repository.files.fields.BrokerErrorLog << traceback_string
            )

    @staticmethod
    def get_update_expr(upload: typing.Dict[typing.AnyStr, typing.Any]) -> typing.Tuple:
        ret = (
            Repository.files.fields.NumOfChunksCompleted << upload.get(
                Repository.files.fields.NumOfChunksCompleted.__name__),
            Repository.files.fields.SizeUploaded << upload.get(Repository.files.fields.SizeUploaded.__name__),
            Repository.files.fields.Status << upload.get(Repository.files.fields.Status.__name__, 0),
            Repository.files.fields.CloudId << upload.get(Repository.files.fields.CloudId.__name__),
            Repository.files.fields.SizeInHumanReadable << upload.get(
                Repository.files.fields.SizeInHumanReadable.__name__),
            Repository.files.fields.MainFileId << upload.get(Repository.files.fields.MainFileId.__name__),
            Repository.files.fields.NumOfChunksCompleted << upload.get(
                Repository.files.fields.NumOfChunksCompleted.__name__),
            Repository.files.fields.SizeUploaded << upload.get(Repository.files.fields.SizeUploaded.__name__),
            Repository.files.fields.FileName << upload.get(Repository.files.fields.FileName.__name__),
            Repository.files.fields.SizeInBytes << upload.get(Repository.files.fields.SizeInBytes.__name__),
            Repository.files.fields.ChunkSizeInKB << upload.get(Repository.files.fields.ChunkSizeInKB.__name__),
            Repository.files.fields.FileExt << upload.get(Repository.files.fields.FileExt.__name__),
            Repository.files.fields.MimeType << upload.get(Repository.files.fields.MimeType.__name__),
            Repository.files.fields.OriginalFileExt << (upload.get(Repository.files.fields.OriginalFileExt.__name__) or
                                                        upload.get(Repository.files.fields.FileExt.__name__))
        )
        if upload.get(Repository.files.fields.VersionNumber.__name__):
            ret=ret.__add__((Repository.files.fields.VersionNumber << upload.get(Repository.files.fields.VersionNumber.__name__),))
        if upload.get(Repository.files.fields.MimeType.__name__):
            ret = ret.__add__(
                (Repository.files.fields.MimeType << upload.get(Repository.files.fields.MimeType.__name__),))
        return ret

    def update_upload(self, app_name: str, upload_id: str, upload: typing.Dict[typing.AnyStr, typing.Any],
                      update_cache_only: bool = False):
        """
        Update register info to cache and datbase
        @param app_name:
        @param upload_id:
        @param upload:
        @param update_cache_only:
        @return:
        """
        self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, upload)
        if update_cache_only:
            return
        ret = Repository.files.app(app_name).context.update(
            Repository.files.fields.id == upload_id,
            *FileUtilService.get_update_expr(upload)
        )
        return ret

    async def save_file_async(self, app_name: str, content, upload, index, pool: ThreadPoolExecutor):
        upload_id = upload["_id"]
        if not isinstance(WORKERS.get(upload_id), dict):
            WORKERS[upload_id] = dict(executor=ThreadPoolExecutor(max_workers=MAX_WORKERS), tasks=[])

        start = datetime.utcnow()

        data = await content.read()
        file_size = len(data)

        def running(data, upload, update_upload, index):

            try:
                real_file_location = upload["real_file_location"]

                dir_of_chunks = f"{real_file_location}.chunks.uploading"
                os.makedirs(dir_of_chunks, exist_ok=True)
                chunk_file_path = os.path.join(dir_of_chunks, f"{index}")
                with cy_open_file(chunk_file_path, "wb") as fs:
                    fs.write(data)
                del data
                _, _, files = list(os.walk(dir_of_chunks))[0]
                upload["SizeUploaded"] = sum([os.stat(os.path.join(dir_of_chunks, f)).st_size for f in files])
                upload["SizeUploadedInHumanReadable"] = naturalsize(upload["SizeUploaded"])
                if upload["SizeInBytes"] == upload["SizeUploaded"]:
                    if os.path.isdir(f"{real_file_location}.chunks"):
                        os.rename(f"{real_file_location}.chunks", f"{real_file_location}.chunks.deleting")
                    if os.path.isdir(f"{real_file_location}.chunks.uploading"):
                        os.rename(f"{real_file_location}.chunks.uploading", f"{real_file_location}.chunks")
                    if os.path.isdir(f"{real_file_location}.chunks.deleting"):
                        shutil.rmtree(f"{real_file_location}.chunks.deleting", ignore_errors=True)
                    upload["Status"] = 1
                    upload["SizeInHumanReadable"] = naturalsize(upload["SizeUploaded"])
                    update_upload(app_name, upload["_id"], upload)
                    upload_data_from_mongo_db = Repository.files.app(app_name).context.find_one(
                        Repository.files.fields.Id == upload["_id"]
                    )
                    self.cloud_storage_sync_service.do_sync(app_name, upload_data_from_mongo_db)
                    self.post_msg_upload_file(app_name=app_name, data=upload_data_from_mongo_db,
                                              upload_id=upload["_id"])
                    del WORKERS[upload["_id"]]

                else:
                    update_upload(app_name, upload["_id"], upload)


            except:
                upload["error"] = traceback.format_exc()

        async def run_async(data, upload, update_upload, index):
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, running, data, upload, update_upload, index)

        upload["NumOfChunksCompleted"] = index + 1
        size_in_human_readable = naturalsize(upload[Repository.files.fields.SizeInBytes.__name__])

        upload["SizeUploaded"] = upload.get("SizeUploaded", 0) + file_size
        size_uploaded_in_human_readable = naturalsize(upload.get("SizeUploaded", 0))
        percent = math.ceil((float(upload["NumOfChunksCompleted"]) / float(upload["NumOfChunks"])) * 100)
        # exp = future.exception()

        tasks = WORKERS[upload_id].get("tasks")
        run_in_task = True
        if len(WORKERS[upload_id].get("tasks")) < MAX_WORKERS:
            tasks.append(asyncio.create_task(run_async(data, upload, self.update_upload, index)))
        else:
            async def wait_for():
                await asyncio.gather(*WORKERS[upload_id].get("tasks"))
                WORKERS[upload_id]["tasks"] = []
                print("done")

            await asyncio.create_task(wait_for())
            await run_async(data, upload, self.update_upload, index)
            run_in_task = False

        return dict(
            Data=dict(
                SizeInHumanReadable=size_in_human_readable,
                SizeUploadedInHumanReadable=size_uploaded_in_human_readable,
                Percent=percent,
                ProcessingTime=(datetime.utcnow() - start).total_seconds() * 1000,
                NumOfChunksCompleted=upload["NumOfChunksCompleted"],
                RunInTask=run_in_task
            )
        )



    async def register_upload_create_async(self, from_host, app_name, register_data: dict):
        context = Repository.files.app(app_name).context
        upload_id = register_data.get("UploadId") or str(uuid.uuid4())

        file_name = register_data["FileName"].replace('/', '_').replace("?", "_").replace("#", '_')
        mime_type, _ = mimetypes.guess_type(file_name)

        web_file_name = file_name.replace('/', '_')
        chunk_size_in_kb = register_data["ChunkSizeInKB"]
        file_size = register_data["FileSize"]
        is_public = register_data["IsPublic"]
        privileges = register_data["Privileges"]
        meta_data = register_data["meta_data"]
        register_on = datetime.utcnow()
        formatted_date = register_on.strftime("%Y/%m/%d")

        file_name_only = pathlib.Path(file_name).stem
        file_ext = pathlib.Path(file_name).suffix
        file_type = "unknown"
        if file_ext:
            file_type = file_ext[1:4]
        human_readable_size = naturalsize(file_size)
        # "FullFileName": "6c08cbfc-6832-49a8-9def-c2e99d868144/L_846C.tmp.PNG"
        chunk_size_in_bytes = chunk_size_in_kb * 1024
        num_of_chunks = file_size // chunk_size_in_bytes + 1 if file_size % chunk_size_in_bytes > 0 else 0
        main_file_id = f"local://{app_name}/{formatted_date}/{file_type}/{upload_id}/{file_name.lower()}"
        privileges, _ = self.elastic_search_util_service.create_privileges(register_data.get('Privileges') or {})
        meta_data = register_data.get('meta_data') or {}
        googlePath = f'{register_data["googlePath"]}/{register_data["FileName"]}' if register_data.get(
            "googlePath") else None
        insert_data = [
            Repository.files.fields.id << upload_id,
            Repository.files.fields.FileName << file_name,
            Repository.files.fields.MainFileId << main_file_id,
            Repository.files.fields.FileExt << file_ext[1:].lower(),
            Repository.files.fields.StorageType << register_data["storageType"],
            Repository.files.fields.Status << 0,
            Repository.files.fields.RegisterOn << register_on,
            Repository.files.fields.SizeInBytes << file_size,
            Repository.files.fields.ChunkSizeInBytes << chunk_size_in_bytes,
            Repository.files.fields.ChunkSizeInKB << chunk_size_in_kb,
            Repository.files.fields.FileNameLower << file_name.lower(),
            Repository.files.fields.FullFileName << f"{upload_id}/{file_name.lower()}",
            Repository.files.fields.NumOfChunks << num_of_chunks,
            Repository.files.fields.MimeType << mime_type,
            Repository.files.fields.FullFileNameLower << f"{upload_id}/{file_name.lower()}",
            Repository.files.fields.StoragePath << f"local://{main_file_id}",
            Repository.files.fields.IsPublic << register_data.get("IsPublic", True),
            Repository.files.fields.FullFileNameWithoutExtenstion << f"{upload_id}/{file_name_only}",
            Repository.files.fields.FullFileNameWithoutExtenstionLower << f"{upload_id}/{file_name_only}".lower(),
            Repository.files.fields.Privileges << privileges,
            Repository.files.fields.OriginalFileExt<<file_ext[1:].lower()
        ]
        if googlePath:
            insert_data += [Repository.files.fields.FullPathOnCloud << googlePath]
        ret = await context.insert_one_async(*insert_data)

        t = datetime.utcnow()
        upload = await context.find_one_async(
            Repository.files.fields.id == upload_id
        )

        self.elastic_search_util_service.create_or_update_privileges(
            app_name=app_name,
            upload_id=upload_id,
            data_item=upload,
            privileges=privileges,
            meta_info=meta_data
        )
        print((datetime.utcnow() - t).total_seconds())
        ret_data = dict(
            NumOfChunks=num_of_chunks,
            ChunkSizeInBytes=chunk_size_in_bytes,
            UploadId=upload_id,
            MimeType=mime_type,
            RelUrlOfServerPath=f"api/{app_name}/file/{upload_id}/{file_name.lower()}",
            SizeInHumanReadable=human_readable_size,
            UrlOfServerPath=f"{from_host}/api/{app_name}/{upload_id}/{file_name.lower()}",
            OriginalFileName=file_name,
            FileSize=file_size,
            UpdateESTime=(datetime.utcnow() - t).total_seconds()
        )
        return dict(
            Data=ret_data
        )

    async def register_upload_update_async(self, app_name, from_host, register_data):
        """

        @param app_name:
        @param from_host:
        @param register_data: Register dta is a data from client
        @return:
        """
        upload_data = await self.get_upload_by_upload_id_async(
            app_name=app_name,
            upload_id=register_data.get("UploadId")
        )
        if upload_data is None:
            return dict(
                Error=dict(
                    Code="FileNotFound",
                    Message=f"{register_data['UploadId']} is no longer in {app_name}"
                )
            )
        """
            {
                "Data": {
                    "NumOfChunks": 1,
                    "ChunkSizeInBytes": 10485760,
                    "UploadId": "a3fbefde-fa32-44ed-97d9-f65599a82653",
                    "ServerFilePath": "a3fbefde-fa32-44ed-97d9-f65599a82653.jpg",
                    "MimeType": "image/jpeg",
                    "RelUrlOfServerPath": "api/masantest/file/a3fbefde-fa32-44ed-97d9-f65599a82653/z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg",
                    "SizeInHumanReadable": "770.2 kB",
                    "UrlOfServerPath": "http://172.16.7.99/lvfile/api/masantest/file/a3fbefde-fa32-44ed-97d9-f65599a82653/z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg",
                    "OriginalFileName": "z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg",
                    "UrlThumb": "http://172.16.7.99/lvfile/api/masantest/thumb/a3fbefde-fa32-44ed-97d9-f65599a82653/z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg.webp",
                    "RelUrlThumb": "api/masantest/thumb/a3fbefde-fa32-44ed-97d9-f65599a82653/z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg.webp",
                    "FileSize": 770250,
                    "SearchEngineInsertTimeInSecond": 0.017286
                },
                "Error": null
            }
        """
        """
        {
            "Data":{
                    "FileName":"z5416308293225_ac0010b93438d1ee518532ea338201c1 _1_ _1_.jpg",
                    "FileSize":770250,"ChunkSizeInKB":10240,
                    "IsPublic":true,
                    "ThumbConstraints":"700,350,200,120",
                    "Privileges":[],"meta_data":{},
                    "storageType":"local","onedriveScope":"anonymous","encryptContent":true,"googlePath":"long-test-2024-07-09"}}
        """
        file_size_in_bytes = register_data["FileSize"]
        chunk_size_in_kb = register_data[Repository.files.fields.ChunkSizeInKB.__name__]
        version_number = upload_data.get(Repository.files.fields.VersionNumber.__name__) or 0
        version_number += 1
        upload_data[Repository.files.fields.VersionNumber.__name__] = version_number
        chunk_size_in_bytes = chunk_size_in_kb * 1024
        m_type, _ = mimetypes.guess_type(register_data["FileName"])
        num_of_chunks = file_size_in_bytes // chunk_size_in_bytes + (
            1 if file_size_in_bytes % chunk_size_in_bytes > 0 else 0)
        await Repository.files.app(app_name).context.update_async(
            Repository.files.fields.id == register_data["UploadId"],
            Repository.files.fields.SizeInBytes << file_size_in_bytes,
            Repository.files.fields.SizeInHumanReadable << naturalsize(file_size_in_bytes),
            Repository.files.fields.Status << 0,
            Repository.files.fields.NumOfChunksCompleted << 0,
            Repository.files.fields.NumOfChunks << num_of_chunks,
            Repository.files.fields.ChunkSizeInKB << chunk_size_in_kb,
            Repository.files.fields.ChunkSizeInBytes << chunk_size_in_bytes,
            Repository.files.fields.SizeUploaded << 0,
            Repository.files.fields.NumOfChunksCompleted << 0,
            Repository.files.fields.MimeType << m_type,
            Repository.files.fields.VersionNumber << version_number,
            Repository.files.fields.OriginalFileExt << (upload_data.get(Repository.files.fields.OriginalFileExt.__name__)
                                                        or upload_data.get(Repository.files.fields.FileExt.__name__))

        )
        key = f"{self.cache_type}/{app_name}/{register_data['UploadId']}"
        self.memcache_service.remove(key)
        self.clear_cache_file(app_name, upload_id=register_data['UploadId'])

        return dict(
            Data=dict(
                NumOfChunks=num_of_chunks,
                ChunkSizeInBytes=chunk_size_in_bytes,
                UploadId=register_data["UploadId"],
                ServerFilePath=register_data["UploadId"] + "." + upload_data[Repository.files.fields.FileExt],
                SizeInHumanReadable=naturalsize(file_size_in_bytes)
            )
        )

    async def register_upload_async(self, from_host, app_name, register_data: typing.Dict[str, typing.Any]):
        """
        Create nw upload before upload content
        :param from_host: when call from FastAOI controller host url of this web API must put here
        :param app_name: tenant name
        :param register_data: data from client
        :return:
        """
        try:
            if register_data.get("UploadId"):
                """
                If register upload with specific UploadID value. That mean we are updating content of material
                1- The first we need to reset all status of Upload Info except status
                """
                upload_item = self.get_upload(
                    app_name=app_name,
                    upload_id=register_data.get("UploadId")
                )
                if upload_item is None:
                    raise RegisterUploadException(Code="System",
                                                  Message="The material was delete or move to another location")
                upload_item[Repository.files.fields.SizeUploaded.__name__] = 0
                file_size: int = register_data.get("FileSize")
                chunk_size_in_kb: int = register_data.get("ChunkSizeInKB")
                chunk_size = chunk_size_in_kb * 1024
                num_of_chunks = (file_size // chunk_size) + (1 if file_size % chunk_size > 0 else 0)
                file_name = register_data.get("FileName")
                file_ext = pathlib.Path(file_name).suffix[1:].lower()
                upload_item[Repository.files.fields.NumOfChunksCompleted.__name__] = 0
                upload_item[Repository.files.fields.NumOfChunks.__name__] = num_of_chunks
                upload_item[Repository.files.fields.Status.__name__] = 0
                upload_item[Repository.files.fields.ChunkSizeInKB.__name__] = chunk_size_in_kb
                upload_item[Repository.files.fields.ChunkSizeInBytes.__name__] = chunk_size
                upload_item[Repository.files.fields.SizeInBytes.__name__] = file_size
                upload_item[Repository.files.fields.FileExt.__name__] = file_ext
                upload_item[Repository.files.fields.FileName.__name__] = file_name
                if not upload_item.get(Repository.files.fields.OriginalFileExt.__name__):
                    upload_item[Repository.files.fields.OriginalFileExt.__name__]=file_ext
                mime_type,_ = mimetypes.guess_type(file_name)
                upload_item[Repository.files.fields.MimeType.__name__] = mime_type
                self.update_upload(
                    app_name=app_name,
                    upload=upload_item,
                    upload_id=register_data.get("UploadId")
                )
                return await self.register_upload_update_async(
                    app_name=app_name,
                    from_host=from_host,
                    register_data=register_data
                )
            else:
                return await self.register_upload_create_async(
                    app_name=app_name,
                    from_host=from_host,
                    register_data=register_data
                )

        except Exception as ex:
            return dict(
                Error=dict(
                    Code="System",
                    Message=traceback.format_exc()
                )
            )


    def get_upload(self, app_name, upload_id, cache: bool = True) -> typing.Union[typing.Dict[str, typing.Any],None]:
        """
        Get upload with cache if cache do not contains data with app and upload_id. The method will get from Mongodb if found item cache will be update to cache
        The first get data from cache if cache is True, get directly from db instead
        :param app_name:
        :param upload_id:
        :return:
        """
        if cache:
            data = self.memcache_service.get_dict("v2/" + app_name + "/" + upload_id)
            if isinstance(data, dict) and not data.get("real_file_location"):
                real_file_location = os.path.join(config.file_storage_path.replace('/', os.sep),
                                                  data[Repository.files.fields.MainFileId.__name__].split("://")[1].replace(
                                                      '/', os.path.sep)).__str__()
                data["real_file_location"] = real_file_location
                data["real_file_dir"] = pathlib.Path(real_file_location).parent.__str__()
                self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, data)
            if not data:
                ret_upload = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.id == upload_id
                )
                if ret_upload is None:
                    return None
                else:
                    data = ret_upload.to_json_convertable()
                    file_name = ret_upload[Repository.files.fields.FileName]
                    file_ext = pathlib.Path(file_name).suffix

                    main_file_id = data.get(Repository.files.fields.MainFileId.__name__)
                    if not main_file_id:
                        return ret_upload
                    if bson.ObjectId.is_valid(main_file_id):
                        """
                        Still support load file in MongoDb if main_file_id is the id of GridFS
                        """
                        real_file_location = f"mongo://{main_file_id}"
                    elif "://" in main_file_id:
                        real_file_location = os.path.join(config.file_storage_path.replace('/', os.sep),
                                                          main_file_id.split("://")[1].replace('/', os.path.sep)).__str__()
                        if not os.path.isfile(real_file_location) and data.get(
                                Repository.files.fields.StoragePath.__name__):
                            real_file_location = os.path.join(config.file_storage_path.replace('/', os.sep),
                                                              main_file_id.split("://")[1].replace('/',
                                                                                                   os.path.sep)).__str__()
                    else:
                        return None

                    data["real_file_location"] = real_file_location
                    data["real_file_dir"] = pathlib.Path(real_file_location).parent.__str__()
                    data[Repository.files.fields.NumOfChunksCompleted.__name__] = data.get(
                        Repository.files.fields.NumOfChunksCompleted.__name__) or 0
                    data[Repository.files.fields.SizeUploaded.__name__] = data.get(
                        Repository.files.fields.SizeUploaded.__name__) or 0
                    if not real_file_location.startswith("mongo://"):
                        os.makedirs(data["real_file_dir"], exist_ok=True)
                        self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, data)
            return data

        else:
            upload = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.id == upload_id
            )
            if upload is None:
                return None
            else:
                data = upload.to_json_convertable()
                file_name = upload[Repository.files.fields.FileName]
                file_ext = pathlib.Path(file_name).suffix
                file_type = file_ext[1:4] if file_ext else "unknown"

                real_file_location = os.path.join(config.file_storage_path,
                                                  data["MainFileId"].split("://")[1]).__str__()
                data["real_file_location"] = real_file_location
                data["real_file_dir"] = pathlib.Path(real_file_location).parent.__str__()
                data["NumOfChunksCompleted"] = data.get("NumOfChunksCompleted") or 0
                data["SizeUploaded"] = data.get("SizeUploaded") or 0
                os.makedirs(data["real_file_dir"], exist_ok=True)
                self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, data)
            return data


    async def get_content_from_local_async(self, request, app_name, upload_id, content_type, upload):
        """
        get content from local path
        :param request:
        :param app_name:
        :param upload_id:
        :param content_type:
        :param upload:
        :return:
        """
        file_path = await self.get_physical_path_async(
            app_name=app_name,
            upload_id=upload_id
        )

        if file_path is None:
            raise FileNotFoundError()
        if file_path.startswith("mongo://"):
            fs = self.get_fs_mongo(app_name, file_path.split("://")[1])
            ret = await streaming_async(
                fs, request, content_type, streaming_buffering=1024 * 4 * 3 * 8
            )
            ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            if request.query_params.get('download') is not None:
                ret.headers["Content-Disposition"] = f"attachment; filename={upload['FileName']}"
            return ret
        else:
            fs = cy_open_file(file_path, "rb")
            ret = await streaming_async(
                fs, request, content_type, streaming_buffering=1024 * 4 * 3 * 8
            )
            ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            if request.query_params.get('download') is not None:
                ret.headers["Content-Disposition"] = f"attachment; filename={upload['FileName']}"
            return ret


    def get_fs_mongo(self, app_name, file_id):
        db = Repository.files.app(app_name).context.collection.database
        from gridfs import GridFS
        fs_obj = GridFS(db)
        if not isinstance(file_id, bson.ObjectId):
            file_id = bson.ObjectId(file_id)
        fs = fs_obj.get(file_id)
        return fs


    async def get_content_from_google_drive_async(self, request, app_name, upload_id, content_type, upload):
        if upload.get("CloudId"):
            """
            if sync to google is finished 
            """
            ret = await self.g_drive_service.get_content_async(
                app_name=app_name,
                client_file_name=upload["FileName"],
                upload_id=upload_id,
                cloud_id=upload["CloudId"],
                request=request,
                content_type=content_type,
                download_only=request.query_params.get('download') is not None
            )
            return ret
        else:
            """
            is still holding in local 
            """
            return await self.get_content_from_local_async(
                app_name=app_name,
                upload_id=upload_id,
                content_type=content_type,
                request=request,
                upload=upload
            )


    async def get_file_content_async(self, request, app_name: str, directory: str):
        upload_id = directory.split('/')[0]
        upload = await self.get_upload_async(app_name, upload_id)
        if upload is None:
            raise FileNotFoundError()
        content_type, _ = mimetypes.guess_type(directory)
        content_type = upload.get("MimeType") or content_type
        if not upload:
            raise FileNotFoundError(f"{app_name}/{directory} was not found")
        storage_type = upload.get(Repository.files.fields.StorageType.__name__, "local")
        if storage_type == "local":
            return await self.get_content_from_local_async(
                app_name=app_name,
                upload_id=upload_id,
                content_type=content_type,
                request=request,
                upload=upload
            )
        if storage_type == "google-drive":
            try:
                return await self.get_content_from_google_drive_async(
                    app_name=app_name,
                    upload_id=upload_id,
                    content_type=content_type,
                    request=request,
                    upload=upload
                )
            except:
                upload = await self.get_upload_async(app_name, upload_id, from_cache=False)
                return await self.get_content_from_google_drive_async(
                    app_name=app_name,
                    upload_id=upload_id,
                    content_type=content_type,
                    request=request,
                    upload=upload
                )

    def get_physical_path(self, app_name: str, upload_id: str):
        """

        @param app_name:
        @param upload_id:
        @return:
        """
        upload = self.get_upload(app_name, upload_id)
        if upload is None:
            return None

        ret = upload["real_file_location"]
        if not os.path.isfile(ret):
            """
            Fix by update version
            """
            directory = pathlib.Path(ret).parent.__str__()
            if not os.path.isdir(directory):
                return ret
            filename = "data"
            if upload.get(Repository.files.fields.FileExt.__name__):
                filename = filename + "." + upload.get(Repository.files.fields.FileExt.__name__)
            ret = os.path.join(directory,
                               f'{filename}-version-{upload.get(Repository.files.fields.VersionNumber.__name__, 1)}')
            if os.path.isfile(ret):
                upload[Repository.files.fields.MainFileId.__name__] = self.generate_main_file_id(app_name, upload, upload[
                    Repository.files.fields.StorageType.__name__], upload[Repository.files.fields.VersionNumber.__name__])
                upload["real_file_location"] = ret
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id == upload_id,
                    Repository.files.fields.MainFileId << upload[Repository.files.fields.MainFileId.__name__]
                )
                return ret

        if not os.path.isfile(ret):
            ret = ret.lower().replace('(', '_').replace(')', '_')
            if os.path.isfile(ret):
                upload["real_file_location"] = ret
                self.update_upload(app_name=app_name, upload_id=upload_id, upload=upload, update_cache_only=True)
                return ret
        if not os.path.isfile(ret):
            if os.path.isdir(f'{upload["real_file_location"]}.chunks'):
                return f'{upload["real_file_location"]}.chunks'
        return ret
    async def get_physical_path_async(self, app_name: str, upload_id: str):
        """

        @param app_name:
        @param upload_id:
        @return:
        """
        return self.get_physical_path(app_name,upload_id)


    def clear_cache_file(self, app_name, upload_id):
        self.memcache_service.remove(f"get_upload/{app_name}/{upload_id}")


    async def get_upload_async(self, app_name, upload_id, from_cache=True) -> typing.Union[typing.Dict[str, typing.Any],None]:
        if from_cache:
            ret = self.memcache_service.get_dict(f"get_upload/{app_name}/{upload_id}")
            if isinstance(ret, dict):
                return ret
            data = await Repository.files.app(app_name).context.find_one_async(Repository.files.fields.id == upload_id)
            if not data:
                return None
            else:
                ret = data.to_json_convertable()
                self.memcache_service.set_dict(f"get_upload/{app_name}/{upload_id}", ret)
                return ret
        else:
            data = await Repository.files.app(app_name).context.find_one_async(Repository.files.fields.id == upload_id)
            if not data:
                return None
            else:
                ret = data.to_json_convertable()
                self.memcache_service.set_dict(f"get_upload/{app_name}/{upload_id}", ret)
                return ret


    async def get_upload_by_upload_id_async(self, app_name, upload_id):
        return await Repository.files.app(app_name).context.find_one_async(
            Repository.files.fields.Id == upload_id
        )


    async def save_file_single_thread_async(self,
                                            app_name: str,
                                            upload_id: str,
                                            chunk_index: int,
                                            content_part) -> typing.Union[typing.Dict[str, typing.Any],None]:
        upload_item = self.get_upload(
            app_name=app_name,
            upload_id=upload_id
        )
        file_size_in_bytes = upload_item.get(Repository.files.fields.SizeInBytes.__name__)
        chunk_size_in_kb = upload_item.get(Repository.files.fields.ChunkSizeInKB.__name__)
        num_of_chunks = upload_item.get(Repository.files.fields.NumOfChunks.__name__)
        version_number = (upload_item.get(Repository.files.fields.VersionNumber.__name__) or 0)+1
        mode = "wb" if chunk_index == 0 else "ab"
        tem_file_path = self.generate_main_file_path(app_name=app_name, upload=upload_item, version=version_number)
        dir_path = pathlib.Path(tem_file_path).parent.__str__()
        os.makedirs(dir_path, exist_ok=True)
        size_uploaded = upload_item.get(Repository.files.fields.SizeUploaded.__name__, 0)
        with cy_open_file(tem_file_path, mode, encrypt=True, file_size=file_size_in_bytes, chunk_size_in_kb=chunk_size_in_kb) as fs:
            fs.write(content_part)

        if num_of_chunks - 1 == chunk_index:
            """
            Finished set real location of file
            """
            upload_item[Repository.files.fields.Status.__name__] =version_number
            upload_item[Repository.files.fields.VersionNumber.__name__] = 1
            upload_item[Repository.files.fields.MainFileId.__name__] = self.generate_main_file_id(
                app_name=app_name,
                upload=upload_item,
                storage_type="local",
                version=version_number
            )
            upload_item[Repository.files.fields.VersionNumber.__name__] = version_number
            file_name = upload_item[Repository.files.fields.FileName.__name__]
            m_type, _ = mimetypes.guess_type(file_name)
            upload_item["real_file_location"] = tem_file_path
            upload_item[Repository.files.fields.MimeType.__name__] = m_type
        num_of_chunks_completed = upload_item.get(Repository.files.fields.NumOfChunksCompleted.__name__, 0)
        num_of_chunks_completed += 1
        upload_item[Repository.files.fields.NumOfChunksCompleted.__name__] = num_of_chunks_completed
        upload_item[Repository.files.fields.SizeUploaded.__name__] = size_uploaded + len(content_part)
        del content_part
        self.update_upload(
            app_name=app_name,
            upload_id=upload_item.get("_id"),
            upload=upload_item,

        )
        return upload_item


    def generate_main_file_id(self, app_name: str, upload: typing.Dict[str, typing.Any], storage_type: str,
                              version: typing.Union[int,None]) -> str:
        """
        This method generate a info of file location
        1- For local: the path start with local://
        2- For google drive path start with google-drive://
        3 - ..

        @param app_name:
        @param upload:
        @param storage_type: start of return value will get value from this argument. Exp: storage_type is 'local' return value will be local://
        @param version: since 08-21-2004 we discovery that error will be occur if file name change while it was accessing by  any unexpected process. The version of upload content is a solution
        @return:
        """
        file_name = "data"
        if upload.get(Repository.files.fields.FileExt.__name__):
            file_name = f'{file_name}.{upload.get(Repository.files.fields.FileExt.__name__)}'
        ext_file = "unknown"
        if upload.get(Repository.files.fields.OriginalFileExt.__name__):
            ext_file = upload.get(Repository.files.fields.OriginalFileExt.__name__)[0:3]
        elif upload.get(Repository.files.fields.FileExt.__name__):
            ext_file = upload.get(Repository.files.fields.FileExt.__name__)[0:3]
        registered_on_iso: str = upload.get(Repository.files.fields.RegisterOn.__name__)
        registered_on = datetime.fromisoformat(registered_on_iso)
        registered_on_str = registered_on.strftime("%Y/%m/%d")
        if version is None:
            return f'{storage_type}://{app_name}/{registered_on_str}/{ext_file}/{upload.get("_id")}/{file_name}'
        else:
            return f'{storage_type}://{app_name}/{registered_on_str}/{ext_file}/{upload.get("_id")}/{file_name}-version-{version}'


    def generate_main_file_path(self, app_name: str, upload: typing.Dict[str, typing.Any], version: typing.Union[int,None]) -> str:
        # file_name:str = upload.get(Repository.files.fields.FileName.__name__)
        file_name = "data"
        if upload.get(Repository.files.fields.FileExt.__name__):
            file_name = f'{file_name}.{upload.get(Repository.files.fields.FileExt.__name__)}'
        file_name = file_name.lower().replace('(', '_').replace(')', '_')
        ext_file = "unknown"

        if upload.get(Repository.files.fields.OriginalFileExt.__name__):
            ext_file = upload.get(Repository.files.fields.OriginalFileExt.__name__)[0:3]
        elif upload.get(Repository.files.fields.FileExt.__name__):
            ext_file = upload.get(Repository.files.fields.FileExt.__name__)[0:3]
        registered_on_iso: str = upload.get(Repository.files.fields.RegisterOn.__name__)
        registered_on = datetime.fromisoformat(registered_on_iso)
        registered_on_str = registered_on.strftime("%Y/%m/%d")
        if version is None:
            return f'{config.file_storage_path}/{app_name}/{registered_on_str}/{ext_file}/{upload.get("_id")}/{file_name}'.replace(
                '/', os.path.sep)
        else:
            return f'{config.file_storage_path}/{app_name}/{registered_on_str}/{ext_file}/{upload.get("_id")}/{file_name}-version-{version}'.replace(
                '/', os.path.sep)


    async def do_copy_async(self, app_name, upload_id, request):
        """
        Re-modify on 2024-06-26 to fix Masant requirement
        :param app_name:
        :param upload_id:
        :param request:
        :return:
        """
        document_context = Repository.files.app(app_name)
        item = await document_context.context.find_one_async(
            Repository.files.fields.id==upload_id
        )

        if item is None:
            return None

        source_file_path = await self.get_physical_path_async(app_name, upload_id)

        item.id = str(uuid.uuid4())
        item.RegisterOn = datetime.utcnow()
        item[document_context.fields.FullFileName] = f"{item.id}/{item[document_context.fields.FileName]}"
        item[document_context.fields.FullFileNameLower] = item[document_context.fields.FullFileName].lower()
        item[document_context.fields.Status] = 1
        item[document_context.fields.PercentageOfUploaded] = 100
        item[document_context.fields.MarkDelete] = False
        item.ServerFileName = f"{item.id}.{item[document_context.fields.FileExt]}"

        item[document_context.fields.RegisteredBy] = "root"


        # Copy all file in directory of source_file_path into directory of dest_file_path

        source_dir = os.path.dirname(source_file_path)
        dir_of_file_type = pathlib.Path(source_file_path).parent.parent.stem
        dest_dir = os.path.join(config.file_storage_path,app_name,item.RegisterOn.strftime("%Y/%m/%d"),dir_of_file_type,item.id)
        os.makedirs(dest_dir, exist_ok=True)
        for file_name in os.listdir(source_dir):
            source_file_path = os.path.join(source_dir, file_name)
            if not os.path.isfile(source_file_path):
                continue
            dest_file_path = os.path.join(dest_dir, file_name)

            # Copy the file, preserving metadata
            shutil.copy2(source_file_path, dest_file_path)



        del item[document_context.fields.MainFileId]
        to_location = item[document_context.fields.FullFileNameLower].lower()
        json_data = item.to_json_convertable()
        main_file_id = self.generate_main_file_id(
            app_name=app_name,
            upload=json_data,
            version=item[Repository.files.fields.VersionNumber] or 1,
            storage_type=item[Repository.files.fields.StorageType]
        )
        item[Repository.files.fields.MainFileId] = main_file_id
        Repository.files.app(app_name).context.insert_one(item)
        return item

    def generate_image_in_process(self,resource_url:str,upload_resource_url:str, resource_ext_file:str):
        """
        This method just send a signal to lib pod for image processing without waiting or track any error
        @param resource_url: the resource of url only run on local
        @param upload_resource_url: the upload url only run on local (upload url is private channel for Pod in k8s or docker contact together never use at public)
        @param resource_ext_file:
        @return:
        """
        if resource_ext_file is None or resource_ext_file=="":
            return
        m_t,_ = mimetypes.guess_type(f"a.{resource_ext_file}")
        def run_in_thread():
            try:
                if resource_ext_file == "pdf":
                    self.remote_caller_service.get_image_from_pdf(
                        download_url=resource_url,
                        upload_url=upload_resource_url
                    )
                elif resource_ext_file in config.ext_office_file:
                    self.remote_caller_service.get_image_from_office(
                        url_of_content=resource_url,
                        url_upload_file=upload_resource_url,
                        url_of_office_to_image_service=config.remote_office
                    )
                elif m_t.startswith("video/"):
                    self.remote_caller_service.get_image_from_video(
                        download_url=resource_url,
                        upload_url=upload_resource_url
                    )
            except:
                self.logs_to_mongodb_service.log_async(
                    error_content=traceback.format_exc(),
                    url="Call remote service"
                )
        threading.Thread(target=run_in_thread).start()


