import datetime
import json
import math
import mimetypes
import os.path
import pathlib
import traceback
import uuid

from fastapi_router_controller import Controller
from urllib.parse import urlencode
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)
from cyx.repository import Repository
from cy_jobs.controllers.base_controller import BaseController
from urllib.parse import quote
router = APIRouter()
controller = Controller(router)
from humanize import naturalsize
from cyx.common import config
import cy_file_cryptor.context
import cy_file_cryptor.wrappers
cy_file_cryptor.context.set_server_cache(config.cache_server)
@controller.resource()
class FilesPushingController(BaseController):
    async def get_upload_async(self, app_name, upload_id):
        data = self.memcache_service.get_dict("v2/"+app_name+"/"+upload_id)
        if not data:
            upload = await Repository.files.app(app_name).context.find_one_async(
                Repository.files.fields.id==upload_id
            )
            if upload is None:
                return None
            else:
                data = upload.to_json_convertable()
                file_name = upload[Repository.files.fields.FileName]
                file_ext = pathlib.Path(file_name).suffix
                file_type = file_ext[1:4] if file_ext else "unknown"

                real_file_location = os.path.join(config.file_storage_path, data["MainFileId"].split("://")[1])
                data["real_file_location"]=real_file_location
                data["real_file_dir"] = pathlib.Path(real_file_location).parent.__str__()
                data["NumOfChunksCompleted"]=data.get("NumOfChunksCompleted") or 0
                data["SizeUploaded"] = data.get("SizeUploaded") or 0
                os.makedirs(data["real_file_dir"],exist_ok=True)
                self.memcache_service.set_dict("v2/"+app_name+"/"+upload_id,data)
        return data
    async def update_upload_async(self, app_name, upload_id, upload):
        self.memcache_service.set_dict("v2/"+app_name+"/"+upload_id,upload)
        ret = await Repository.files.app(app_name).context.update_async(
            Repository.files.fields.id == upload_id,
            Repository.files.fields.NumOfChunksCompleted<<upload["NumOfChunksCompleted"],
            Repository.files.fields.SizeUploaded << upload["SizeUploaded"],
            Repository.files.fields.Status << upload.get("Status",0)
        )
        return ret
    @controller.route.post(
        "/files/push-file", summary="Upload local file"
    )
    async def push_file(self,data:dict=Body()):
        """

        :param data:
        :return:
        """


        """
                {
                    "Data": {
                        "SizeInHumanReadable": "1.9 kB",
                        "SizeUploadedInHumanReadable": "1.9 kB",
                        "Percent": 100.0,
                        "NumOfChunksCompleted": 1
                    },
                    "Error": null
                }
        """
        try:
            upload= await  self.get_upload_async(app_name=data["app_name"],upload_id=data["upload_id"])
            real_file_location=upload["real_file_location"]

            file_size = upload["SizeInBytes"]
            file_path= data["file_path"]
            open_mode="ab" if os.path.isfile(real_file_location) else "wb"

            with open(real_file_location,open_mode,encrypt=True,file_size=file_size,chunk_size_in_kb=1024) as fs:
                with open(file_path,"rb") as fr:
                    data_file = fr.read()
                    fs.write(data_file)
                    upload["SizeUploaded"] = upload.get("SizeUploaded", 0) + len(data_file)
                    del data_file

            self.malloc_service.reduce_memory()

            upload["NumOfChunksCompleted"]=data["index"]+1
            size_in_human_readable = naturalsize(upload[Repository.files.fields.SizeInBytes.__name__])
            size_uploaded_in_human_readable = naturalsize(upload.get("SizeUploaded",0))
            percent = math.ceil((upload.get("SizeUploaded",0)*100/file_size))
            if upload["NumOfChunksCompleted"]==upload["NumOfChunks"]:
                upload["Status"]=1
            ret_update = await self.update_upload_async(app_name=data["app_name"],upload_id=data["upload_id"],upload=upload)

            return dict(
                Data=dict(
                    SizeInHumanReadable=size_in_human_readable,
                    SizeUploadedInHumanReadable=size_uploaded_in_human_readable,
                    Percent=percent
                )
            )
        except:
            return dict(
                Error=dict(
                    Code="system",
                    Message= traceback.format_exc()
                )
            )





