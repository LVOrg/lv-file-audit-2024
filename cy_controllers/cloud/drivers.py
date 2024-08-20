from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Body,
)
from cy_controllers.common.base_controller import BaseController
from cyx.common import config
router = APIRouter()
controller = Controller(router)
from cy_xdoc.auths import Authenticate
import re
@controller.resource()
class CloudDriveController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post(
        path="/api/{app_name}/cloud/drive/available-space",
        tags=["CLOUD"]
    )
    def cloud_drive_available_space(self,app_name:str,cloud_name:str=Body(embed=True)):
        if cloud_name not in config.clouds_support:
            return dict(
                Error=dict(
                    Code="NotSupport",
                    Message = f"'{cloud_name}' was not support"
                )
            )
        is_ready = self.cloud_service_utils.is_ready_for(app_name=app_name,cloud_name=cloud_name)
        if not is_ready:
            return dict(
                Error=dict(
                    Code="NotLink",
                    Message=f"'{cloud_name}' did not bestow '{app_name}'"
                )
            )

        if cloud_name=="Google":
            ret, error = self.cloud_service_utils.drive_service.get_available_space(app_name,cloud_name)
            if error:
                return dict(
                    Error=error
                )
            else:
                return  dict(
                    Data=ret
                )

        raise  NotImplemented("")
