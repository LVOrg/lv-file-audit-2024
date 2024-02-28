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
from cyx.repository import Repository

@controller.resource()
class GlobalSettingsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/global/settings/update")
    async def update_settings_async(self, data: SettingInfo = Body(embed=True)):
        ret =await  self.global_settings_service.update_or_create_async(

            ai_gemini_key= data.AIConfig.Gemini.Key,
            ai_gemini_descrition = data.AIConfig.Gemini.Description,
            ai_gpt_key = data.AIConfig.GPT.Key,
            ai_gpt_description = data.AIConfig.GPT.Description

        )
        return ""
