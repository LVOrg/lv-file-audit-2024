import datetime
import json
import mimetypes
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

@controller.resource()
class FilesController(BaseController):
    """
    This controller delicately serve for file upload data
    return dict structure include data and error
    dict(data=..,error=...)
    if not error,  error is null and hash data, data is null and error is not null instead
    structure of error in below forta:
    error=dict(Message=..., Code=...)
    structure of data:
        "NumOfChunks": 1,
        "ChunkSizeInBytes": 10485760,
        "UploadId": "e7029374-5c05-4d7e-b0f6-b48c0845fab3",
        "ServerFilePath": "e7029374-5c05-4d7e-b0f6-b48c0845fab3.txt",
        "MimeType": "text/plain",
        "RelUrlOfServerPath": "api/lv-docs/file/e7029374-5c05-4d7e-b0f6-b48c0845fab3/docker.txt",
        "SizeInHumanReadable": "8.7 kB",
        "UrlOfServerPath": "http://172.16.7.99/lvfile/api/lv-docs/file/e7029374-5c05-4d7e-b0f6-b48c0845fab3/docker.txt",
        "OriginalFileName": "docker.txt",
        "UrlThumb": "http://172.16.7.99/lvfile/api/lv-docs/thumb/e7029374-5c05-4d7e-b0f6-b48c0845fab3/docker.txt.webp",
        "RelUrlThumb": "api/lv-docs/thumb/e7029374-5c05-4d7e-b0f6-b48c0845fab3/docker.txt.webp",
        "FileSize": 8737,
        "SearchEngineInsertTimeInSecond": 0.000375
    """
    #Not Found http://172.16.13.72:8087/api/files/register/local
    @controller.route.post(
        "/files/register/local", summary="Upload local file"
    )
    async def register_local_async(self,data:dict=Body()):
        try:
            from_host = data["from_host"]
            app_name = data["app_name"]
            context = Repository.files.app(app_name).context
            upload_id = str(uuid.uuid4())
            register_data = json.loads(data["data"])

            file_name= register_data["FileName"].replace('/','_').replace("?","_").replace("#",'_')
            mime_type, _ = mimetypes.guess_type(file_name)


            web_file_name=file_name.replace('/','_')
            chunk_size_in_kb = register_data["ChunkSizeInKB"]
            file_size = register_data["FileSize"]
            is_public = register_data["IsPublic"]
            privileges = register_data["Privileges"]
            meta_data= register_data["meta_data"]
            register_on = datetime.datetime.utcnow()
            formatted_date = register_on.strftime("%Y/%m/%d")

            file_name_only = pathlib.Path(file_name).stem
            file_ext = pathlib.Path(file_name).suffix
            file_type= "unknown"
            if file_ext:
                file_type= file_ext[1:4]
            human_readable_size =naturalsize(file_size)
            #"FullFileName": "6c08cbfc-6832-49a8-9def-c2e99d868144/L_846C.tmp.PNG"
            chunk_size_in_bytes = chunk_size_in_kb*1024
            num_of_chunks = file_size // chunk_size_in_bytes + 1 if file_size % chunk_size_in_bytes>0 else 0
            main_file_id = f"local://{app_name}/{formatted_date}/{file_type}/{upload_id}/{file_name.lower()}"
            upload = await context.insert_one_async(
                Repository.files.fields.id<<upload_id,
                Repository.files.fields.FileName<<file_name,
                Repository.files.fields.MainFileId<<main_file_id,
                Repository.files.fields.FileExt<<file_ext[1:].lower(),
                Repository.files.fields.StorageType<<"local",
                Repository.files.fields.Status<<0,
                Repository.files.fields.RegisterOn<<register_on,
                Repository.files.fields.SizeInBytes<<file_size,
                Repository.files.fields.ChunkSizeInBytes<<chunk_size_in_bytes,
                Repository.files.fields.ChunkSizeInKB<<chunk_size_in_kb,
                Repository.files.fields.FileNameLower<<file_name.lower(),
                Repository.files.fields.FullFileName<< f"{upload_id}/{file_name.lower()}",
                Repository.files.fields.NumOfChunks << num_of_chunks,
                Repository.files.fields.MimeType <<mime_type,
                Repository.files.fields.FullFileNameLower<<f"{upload_id}/{file_name.lower()}"

            )
            ret_data = dict(
                NumOfChunks = num_of_chunks,
                ChunkSizeInBytes=chunk_size_in_bytes,
                UploadId=upload_id,
                MimeType= mime_type,
                RelUrlOfServerPath= f"api/{app_name}/file/{upload_id}/{file_name.lower()}",
                SizeInHumanReadable=human_readable_size,
                UrlOfServerPath = f"{from_host}/api/lv-docs/file/e7029374-5c05-4d7e-b0f6-b48c0845fab3/docker.txt",
                OriginalFileName = file_name,
                FileSize=file_size
            )
            return dict(Data=ret_data)
        except Exception as ex:
            return dict(
                Error= dict(
                    Code="System",
                    Message = traceback.format_exc()
                )
            )