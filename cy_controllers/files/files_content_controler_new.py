import pathlib
import sys
import traceback
import typing
from cyx.repository import Repository
from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)
import gridfs.errors
import cyx.common.msg
from cy_controllers.models.file_contents import (
    UploadInfoResult, ParamFileGetInfo, ReadableParam
)
import fastapi.requests
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse, mimetypes
)

router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
from cyx.common import config
# version2 = config.generation if hasattr(config,"generation") else None
version2=None
@controller.resource()
class FilesContentControllerNew(BaseController):

    @controller.router.get(
        "/api/{app_name}/file/{directory:path}" if version2 else "/api/{app_name}/file-new/{directory:path}" ,
        tags=["FILES-CONTENT"]
    )
    async def get_thumb(self, app_name: str, directory: str):
        return  await self.file_util_service.get_file_content_async(
            app_name=app_name,
            directory=directory,
            request=self.request
        )

    @controller.router.get(
        "/api/{app_name}/thumb/{directory:path}" if version2 else "/api/{app_name}/thumb-new/{directory:path}",
        tags=["FILES-CONTENT"]
    )
    async def get_thumb(self, app_name: str, directory: str):
        print("OK")