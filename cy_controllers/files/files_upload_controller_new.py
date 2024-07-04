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


version2 = config.generation if hasattr(config, "generation") else None

from concurrent.futures import ThreadPoolExecutor




@controller.resource()
class FilesUploadControllerNew(BaseController):
    dependencies = [
        Depends(Authenticate),
        # Depends(ThreadPoolContainer.executor)

    ]

    def __init__(self, request: Request,):

        super().__init__(request)
        self.pool = None


    @controller.route.post(
        "/api/{app_name}/files/upload" if version2 else "/api/{app_name}/files/upload_new", summary="Upload file",
        tags=["FILES"]
    )
    async def upload_async(self,
                           app_name: str,
                           UploadId: Annotated[str, Form()],
                           Index: Annotated[int, Form()],
                           FilePart: Annotated[UploadFile, File()]):
        upload = self.file_util_service.get_upload(app_name=app_name, upload_id=UploadId)
        if upload.get("error"):
            return dict(
                Error=dict(
                    Code="System",
                    Message=upload["error"]
                )
            )

        ret = await self.file_util_service.save_file_async(
            app_name=app_name,
            content=FilePart,
            upload=upload,
            index=Index,
            pool=self.pool
        )
        return ret
