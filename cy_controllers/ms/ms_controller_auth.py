import typing

from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body,
    UploadFile,
    File

)

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

from cy_xdoc.auths import Authenticate


@controller.resource()
class MSAuth(BaseController):
    @controller.router.post(
        path="/api/{app_name}/ms/auth/get-login-url"
    )
    async def one_drive_folder_list(self, app_name: str, scopes: typing.List[str] = Body(...)):
        url, error = self.ms_common_service.get_url(app_name=app_name, scopes=scopes)
