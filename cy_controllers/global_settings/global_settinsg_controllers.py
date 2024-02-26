import typing

import cy_web
from fastapi import (
    APIRouter,
    Depends,
    Body
)
from cy_controllers.common.base_controller import BaseController
import pydantic
from fastapi_router_controller import Controller

router = APIRouter()
controller = Controller(router)
from cy_xdoc.auths import Authenticate
from cy_controllers.models.global_settings import SettingInfo


@controller.resource()
class GlobalSettingsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/global/settings/update")
    async def update_settings(self, data: SettingInfo = Body(embed=True)):
        return ""
