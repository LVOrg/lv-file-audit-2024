import math
import mimetypes
import os
import pathlib
import shutil
import tempfile
import threading
import time
import traceback
import uuid
from datetime import datetime
from humanize import naturalsize
import cy_kit
from cyx.common import config
import asyncio
import aiohttp
from cyx.common import config
import requests
import aiohttp.client_exceptions
from cyx.repository import Repository
from cyx.cache_service.memcache_service import MemcacheServices
from fastapi import FastAPI
from cy_web.cy_web_x import streaming_async
import cy_file_cryptor.wrappers
from concurrent.futures import ThreadPoolExecutor
import asyncio

MAX_WORKERS = 10
WORKERS = dict()


class FileUtilService:
    def __init__(self, memcache_service=cy_kit.singleton(MemcacheServices)):
        self.content_service = config.content_service
        self.memcache_service = memcache_service

    def healthz(self):
        def check():
            try:
                print(f"call {self.content_service}/healthz")
                response = requests.get(f"{self.content_service}/healthz")
                response.raise_for_status()  # Raise an exception for non-200 status codes

                # Process successful response
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
            except:
                print(f"call {self.content_service}/api/healthz was fail")
                return False
            return True

        # ok = check()
        # while not ok:
        #     time.sleep(1)
        #     ok = check()
        return "OK"

    def update_upload(self, app_name, upload_id, upload):
        self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, upload)
        ret = Repository.files.app(app_name).context.update(
            Repository.files.fields.id == upload_id,
            Repository.files.fields.NumOfChunksCompleted << upload["NumOfChunksCompleted"],
            Repository.files.fields.SizeUploaded << upload["SizeUploaded"],
            Repository.files.fields.Status << upload.get("Status", 0)
        )
        return ret

    async def save_file_async(self, app_name: str, content, upload, index, pool: ThreadPoolExecutor):
        upload_id = upload["_id"]
        if not isinstance(WORKERS.get(upload_id), dict):
            WORKERS[upload_id] = dict(executor=ThreadPoolExecutor(max_workers=MAX_WORKERS), tasks=[])

        start = datetime.utcnow()
        # fast_api_path = content.temp_file_path
        data = await content.read()
        file_size = len(data)

        def running(data, upload, update_upload, index):

            try:
                real_file_location = upload["real_file_location"]

                dir_of_chunks = f"{real_file_location}.chunks"
                os.makedirs(dir_of_chunks, exist_ok=True)
                chunk_file_path = os.path.join(dir_of_chunks, f"{index}")
                with open(chunk_file_path, "wb") as fs:
                    fs.write(data)
                del data
                # shutil.move(fast_api_path, chunk_file_path)

                # dest_path = os.path.join(f"{real_file_location}.chunks", pathlib.Path(file_path).name)
                # shutil.move(file_path, dest_path)
                upload["SizeUploaded"] = upload.get("SizeUploaded", 0) + file_size
                upload["SizeUploadedInHumanReadable"] = naturalsize(upload["SizeUploaded"])
                if index + 1 == upload["NumOfChunks"]:
                    upload["Status"] = 1
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

            asyncio.create_task(wait_for())
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

    async def register_local_async(self, from_host, app_name, register_data: dict):
        context = Repository.files.app(app_name).context
        upload_id = str(uuid.uuid4())

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
        #"FullFileName": "6c08cbfc-6832-49a8-9def-c2e99d868144/L_846C.tmp.PNG"
        chunk_size_in_bytes = chunk_size_in_kb * 1024
        num_of_chunks = file_size // chunk_size_in_bytes + 1 if file_size % chunk_size_in_bytes > 0 else 0
        main_file_id = f"local://{app_name}/{formatted_date}/{file_type}/{upload_id}/{file_name.lower()}"
        """
        Repository.files.fields.FileName <<file_name,
        Repository.files.fields.FileExt <<file_ext,
        Repository.files.fields.FileNameLower<<file_name.lower(),
        Repository.files.fields.MainFileId<<f"local://{main_file_id}",
        Repository.files.fields.SyncFromPath << file_path,
        Repository.files.fields.MimeType << mime_type,
        Repository.files.fields.Status<< 1,
        Repository.files.fields.FullFileName << f"{upload_id}/{file_name}",
        Repository.files.fields.FullFileNameLower<< f"{upload_id}/{file_name}".lower(),
        Repository.files.fields.ServerFileName << f"{upload_id}.{file_ext}",
        Repository.files.fields.SizeInBytes << os.stat(file_path).st_size,
        Repository.files.fields.SizeInHumanReadable << humanize.naturalsize(os.stat(file_path).st_size),
        Repository.files.fields.RegisterOn << register_on,
        Repository.files.fields.StorageType<<"local",
        Repository.files.fields.IsPublic << True,
        Repository.files.fields.FullFileNameWithoutExtenstion<<f"{upload_id}/{file_name_only}",
        Repository.files.fields.FullFileNameWithoutExtenstionLower << f"{upload_id}/{file_name_only}".lower(),
        Repository.files.fields.StoragePath<<f"local://{main_file_id}"
        """
        upload = await context.insert_one_async(
            Repository.files.fields.id << upload_id,
            Repository.files.fields.FileName << file_name,
            Repository.files.fields.MainFileId << main_file_id,
            Repository.files.fields.FileExt << file_ext[1:].lower(),
            Repository.files.fields.StorageType << "local",
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

        )
        ret_data = dict(
            NumOfChunks=num_of_chunks,
            ChunkSizeInBytes=chunk_size_in_bytes,
            UploadId=upload_id,
            MimeType=mime_type,
            RelUrlOfServerPath=f"api/{app_name}/file/{upload_id}/{file_name.lower()}",
            SizeInHumanReadable=human_readable_size,
            UrlOfServerPath=f"{from_host}/api/{app_name}/{upload_id}/{file_name.lower()}",
            OriginalFileName=file_name,
            FileSize=file_size
        )
        return ret_data

    async def call_api_async(self, api_path: str, data=None, headers=None) -> dict:
        """Makes an asynchronous POST request to the given URL.

        Args:
            url (str): The URL of the endpoint to send the request to.
            data (dict, optional): The data to send in the request body. Defaults to None.
            headers (dict, optional): Additional headers to include in the request. Defaults to None.

        Returns:
            aiohttp.ClientResponse: The response object from the server.
            :param api_path:
        """
        url = f"{self.content_service}/{api_path}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    return await response.json()  # Parse the JSON response
        except aiohttp.client_exceptions.ClientResponseError as ex:
            return dict(
                Error=dict(
                    Message=f"{ex.message}\n{self.content_service}/{api_path}",
                    Code="RemoteAPICallError"
                )
            )

    async def register_new_upload_local_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/local"
        )
        return ret

    async def register_new_upload_google_drive_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/google-drive"
        )
        return ret

    async def register_new_upload_one_drive_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/one-drive"
        )
        return ret

    async def update_upload_local_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/local/one-drive"
        )
        return ret

    async def update_google_drive_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/update/google-drive"
        )
        return ret

    async def update_upload_one_drive_async(self, app_name, from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/update/one-drive"
        )
        return ret

    async def push_file_async(self, app_name, from_host, file_path, index, upload_id):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                file_path=file_path,
                index=index,
                upload_id=upload_id
            ),
            api_path="files/push-file"
        )
        return ret

    def get_upload(self, app_name, upload_id):
        data = self.memcache_service.get_dict("v2/" + app_name + "/" + upload_id)
        if not data:
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

                real_file_location = os.path.join(config.file_storage_path, data["MainFileId"].split("://")[1])
                data["real_file_location"] = real_file_location
                data["real_file_dir"] = pathlib.Path(real_file_location).parent.__str__()
                data["NumOfChunksCompleted"] = data.get("NumOfChunksCompleted") or 0
                data["SizeUploaded"] = data.get("SizeUploaded") or 0
                os.makedirs(data["real_file_dir"], exist_ok=True)
                self.memcache_service.set_dict("v2/" + app_name + "/" + upload_id, data)
        return data

    async def get_file_content_async(self, request, app_name: str, directory: str):
        file_path = await self.get_physical_path_async(
            app_name=app_name,
            upload_id=directory.split('/')[0]
        )
        content_type, _ = mimetypes.guess_type(directory)
        headers = {"Content-Type": content_type}
        if file_path is None:
            raise FileNotFoundError()
        fs = open(file_path, "rb")
        ret = await streaming_async(
            fs, request, content_type, streaming_buffering=1024 * 4 * 3 * 8
        )
        return ret

    async def get_physical_path_async(self, app_name, upload_id):
        upload = self.get_upload(app_name, upload_id)
        if upload is None:
            return None
        ret = upload["real_file_location"]
        if not os.path.isfile(ret):
            if os.path.isdir(f'{upload["real_file_location"]}.chunks'):
                return f'{upload["real_file_location"]}.chunks'
        return None
