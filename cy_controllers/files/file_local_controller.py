import datetime
import gc
import json
import pathlib
import typing
import uuid

import pydantic
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    UploadFile,
    Form, File, Body,Query
)
from starlette.responses import StreamingResponse
from cy_xdoc.auths import Authenticate
import cy_xdoc.models.files
import cy_kit
from cy_xdoc.services.files import FileServices

from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
from cy_controllers.models.files_upload import (
    UploadChunkResult, ErrorResult, UploadFilesChunkInfoResult
)
import datetime
import mimetypes
import threading
from typing import Annotated
from fastapi.requests import Request
import traceback
import humanize

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService, MongoDbFileStorage
)
from fastapi import responses

from cy_controllers.models import (
    files as controller_model_files
)
from cyx.cache_service.memcache_service import MemcacheServices
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import (
    FileUploadRegisterInfo,
    DataMoveTanent,
    DataMoveTanentParam,
    FileContentSaveData,
    FileContentSaveResult,
    CloneFileResult,
    FileContentSaveArgs,
    ErrorInfo,
    AddPrivilegesResult,
    PrivilegesType,
    CheckoutResource
)

import cy_web
from cyx.repository import Repository
import os
import cyx.common.msg
import inspect
from  cy_web.cy_web_x import streaming_async

@controller.resource()
class FilesLocalController(BaseController):
    @controller.route.get(
        "/api/sys/admin/content-share/{rel_path:path}", summary="",
        response_class=StreamingResponse,
        tags=["LOCAL"]
    )
    async def read_raw_content(self,
                               rel_path:str
                               ) -> None:

        local_share_id= self.request.query_params.get("local-share-id")
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")

        upload_id = pathlib.Path(rel_path).parent.name.__str__()
        app_name = rel_path.split('/')[0]
        server_path = os.path.join(self.config.file_storage_path, rel_path.replace('/', os.path.sep))

        if local_share_id:
            check_data = self.local_api_service.check_local_share_id(
                app_name=app_name,
                local_share_id=local_share_id
            )
            if check_data and isinstance(check_data.UploadId, str) and check_data.UploadId != upload_id:
                if not self.token_verifier.verify(self.share_key, token):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")

        if os.path.isdir(f"{server_path}.chunks"):
            file_name= pathlib.Path(server_path).name.lower()
            return await self.file_util_service.get_file_content_async(self.request, app_name, f"{upload_id}/{file_name}")
        if not os.path.isfile(server_path):

            UploadData = await Repository.files.app(app_name).context.find_one_async(
                Repository.files.fields.id==upload_id
            )
            if UploadData is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            if UploadData.StorageType == "google-drive" and UploadData.CloudId:
                m, _ = mimetypes.guess_type(UploadData.FileName)
                return await self.g_drive_service.get_content_async(
                    app_name=app_name,
                    cloud_id=UploadData.CloudId,
                    client_file_name=UploadData.FileName,
                    request=self.request,
                    upload_id=upload_id,
                    content_type=m

                )
            if UploadData.StorageType == "onedrive" and UploadData.CloudId:
                m, _ = mimetypes.guess_type(UploadData.FileName)
                return await self.azure_utils_service.get_content_async(
                    app_name=app_name,
                    cloud_file_id=UploadData.CloudId,
                    content_type=m,
                    request=self.request,
                    upload_id=upload_id
                )
        else:
            fs = open(server_path, "rb")
            content_type, _ = mimetypes.guess_type(server_path)
            ret = await streaming_async(
                fs, self.request, content_type, streaming_buffering=1024 * 4 * 3 * 8
            )
            ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return ret
        # upload_item = await self.file_util_service.get_upload_by_upload_id_async(app_name=app_name,upload_id=upload_id)
        # if not upload_item:
        #     return  Response(status_code=404,content="Contet was not found")
        # return  await self.file_util_service.get_file_content_async(self.request,app_name,f'{upload_id}/{upload_item["FileNameLower"]}')


    @controller.route.post(
        "/api/sys/admin/content-write/{rel_path:path}", summary="",
        tags=["LOCAL"]
    )

    async def write_raw_content(self,rel_path: str,content: Annotated[UploadFile, File()]):
        import aiofiles
        local_share_id = self.request.query_params.get("local-share-id")
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")

        server_path = os.path.join(self.config.file_storage_path, rel_path.replace('/', os.path.sep))
        server_dir = pathlib.Path(server_path).parent.__str__()
        os.makedirs(server_dir,exist_ok=True)
        async with aiofiles.open(server_path, 'wb') as f:
            while True:
                chunk = await content.read(1024)
                if not chunk:
                    break
                await f.write(chunk)
        return server_path