import datetime
import gc
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
    Form, File, Body
)
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
    PrivilegesType
)

import cy_web
from cyx.repository import Repository
import os
@controller.resource()
class FilesSourceController(BaseController):
    # dependencies = [
    #     Depends(Authenticate)
    # ]

    @controller.router.post("/api/{app_name}/files/update_source/{id}")
    async def update_source_async(self,app_name:str,id:str, content: UploadFile = File(...)):
        data = await Repository.files.app(app_name).context.find_one_async(
            Repository.files.fields.id==id
        )
        if isinstance(data.MainFileId,str) and data.MainFileId.startswith("local://"):
            file_path= os.path.join(self.config.file_storage_path,data.MainFileId.split("://")[1])
            with open(file_path, "wb") as f:
                while contents := content.file.read(1024 * 1024):
                    f.write(contents)
                    # self.broker.emit(
                    #     app_name=app_name,
                    #     message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                    #     data=data
                    # )
        return True
