import datetime
import gc
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
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
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


@controller.resource()
class FilesLocalController(BaseController):
    @controller.route.post(
        "/api/sys/admin/content-share/{rel_path:path}", summary=""
    )
    async def save_raw_content(self,
                               rel_path: str,

                               content: Annotated[UploadFile, File()]

                               ) -> None:
        is_ok = False
        local_share_id = self.request.query_params.get("local-share-id")
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")
        server_path = os.path.join(self.config.file_storage_path, rel_path.replace('/', os.path.sep))
        upload_id = pathlib.Path(rel_path).parent.__str__()
        app_name = rel_path.split('/')[0]
        if local_share_id:
            check_data = self.local_api_service.check_local_share_id(
                app_name=app_name,
                local_share_id=local_share_id
            )
            if check_data and isinstance(check_data.UploadId, str) and check_data.UploadId != upload_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")
            elif not self.token_verifier.verify(self.share_key,token):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")
        try:


            pos = 0
            if self.request.headers.get("Range"):
                range_content = self.request.headers["Range"].split("bytes=")[0]
                pos = int(range_content.split("-")[0])
                if len(range_content.split("-")) == 2:
                    pos_len = int(range_content.split("-")[1]) - pos
            if pos == 0:
                with open(server_path, "wb", encrypt=True, chunk_size_in_kb=1024) as f:
                    while contents := content.file.read(1024 * 1024):
                        f.write(contents)
            else:
                with open(server_path, "ab", encrypt=True, chunk_in_kb=1024) as f:
                    while contents := content.file.read(1024 * 1024):
                        f.write(contents)
        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


        except Exception as e:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @controller.route.get(
        "/api/sys/admin/content-share/{rel_path:path}", summary="", response_class=StreamingResponse
    )
    async def read_raw_content(self,
                               rel_path: str
                               ) -> None:
        import urllib.parse
        local_share_id= self.request.query_params.get(("local-share-id"))
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")
        server_path = os.path.join(self.config.file_storage_path, rel_path.replace('/', os.path.sep))
        upload_id = pathlib.Path(rel_path).parent.__str__()
        app_name = rel_path.split('/')[0]
        if local_share_id:
            check_data = self.local_api_service.check_local_share_id(
                app_name=app_name,
                local_share_id=local_share_id
            )
            if check_data and isinstance(check_data.UploadId, str) and check_data.UploadId != upload_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")
            elif not self.token_verifier.verify(self.share_key, token):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")

        try:


            # Open the file in binary mode
            response_header = None
            pos = 0
            pos_len = 1024 * 4
            content_length = os.path.getsize(server_path)
            response_content_len = content_length
            if self.request.headers.get("Range"):
                range_content = self.request.headers["Range"].split("=")[1]
                print(range_content)
                pos = int(range_content.split("-")[0])
                response_content_len = content_length - pos
                if len(range_content.split("-")) == 2 and range_content.split("-")[1].isnumeric():
                    response_content_len = int(range_content.split("-")[1]) - pos
            response_header = {
                "Accept-Ranges": "bytes",
                "Content-Length": str(response_content_len),
                "Content-Range": F"bytes {pos}-{content_length - 1}/{content_length}"
            }
            fs = open(server_path, "rb")
            #
            fs.seek(pos)
            segment_len = 8192

            def iter_content():

                # Yield file data in chunks for efficient streaming
                data = fs.read(segment_len)
                while data:
                    yield data
                    data = fs.read(segment_len)
                # yield bytes([])

            content_type, _ = mimetypes.guess_type(server_path)
            fx = iter_content()
            print(fx)
            return responses.StreamingResponse(
                content=iter_content(),
                media_type=content_type,
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                headers=response_header
            )


        except FileNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


        except Exception as e:

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))