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
class MSSettings(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.router.post(
        path="/api/{app_name}/ms/settings/update"
    )
    def settings_update(self,app_name:str,tenantId:str=Body(embed=True), clientId:str=Body(embed=True),clientSecret:str=Body(embed=True)):
        return self.ms_common_service.settings_update(
            app_name=app_name,
            tenant_id = tenantId,
            client_id = clientId,
            client_secret=clientSecret,
            request = self.request

        )

    @controller.router.post(
        path="/api/{app_name}/ms/settings/get"
    )
    def settings_get(self, app_name: str, tenantId: str, clientId: str = Body(embed=True),
                        clientSecret: str = Body(embed=True)):

        tenant_id,client_id,client_secret = self.ms_common_service.settings_get(app_name)
        return dict(
            tenantId= tenant_id,
            clientID=client_id,
            clientSecret=client_secret
        )