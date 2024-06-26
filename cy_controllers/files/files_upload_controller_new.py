import datetime
import gc
import os.path

import cy_web
from cyx.common import config
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
    Form, File
)

import bson
from cy_xdoc.auths import Authenticate
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
from cyx.common.msg import MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService, MongoDbFileStorage
)

from cyx.cache_service.memcache_service import MemcacheServices
from cy_controllers.common.base_controller import BaseController


async def get_main_file_id_async(fs):
    st = datetime.datetime.utcnow()
    ret = await fs.get_id_async()
    n = (datetime.datetime.utcnow() - st).total_seconds()
    print(f"get_main_file_id_async={n}")
    return ret

version2 = config.generation if hasattr(config,"generation") else None
@controller.resource()
class FilesUploadControllerNew(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        super().__init__(request)




    @controller.route.post(
        "/api/{app_name}/files/upload" if version2  else "/api/{app_name}/files/upload_new", summary="Upload file",
        tags=["FILES"]
    )
    async def upload_async(self,
                           app_name: str,
                           UploadId: Annotated[str, Form()],
                           Index: Annotated[int, Form()],
                           FilePart: Annotated[UploadFile, File()]):
        tmp_upload_dir = os.path.join(config.file_storage_path,"__temp_upload__",UploadId)
        os.makedirs(tmp_upload_dir,exist_ok=True)
        content_part = await FilePart.read(FilePart.size)
        file_name= f"{Index}"
        file_path = os.path.join(tmp_upload_dir,file_name)
        with open(file_path,"wb") as fs:
            fs.write(content_part)
        del content_part
        self.malloc_service.reduce_memory()
        ret = await self.file_util_service.push_file_async(
            app_name=app_name,
            from_host=cy_web.get_host_url(self.request),
            file_path=file_path,
            index=Index,
            upload_id=UploadId
        )
        return ret




