import datetime
import typing
import cy_docs
from cy_controllers.models.apps import (
    AppInfo,
    AppInfoRegister,
    AppInfoRegisterResult,
    ErrorResult, AppInfoRegisterModel
)
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response, Body
)
from cy_xdoc.auths import Authenticate

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo
from pydantic import BaseModel

class GoogleAuthCredentials(BaseModel):
  client_id: str
  client_secret: str
from fastapi import Body

@controller.resource()
class GoogleSettingsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        self.request = request

    @controller.route.get(
        "/api/{app_name}/google-drive-settings/update", summary="Update settings for google drive"
    )
    def google_drive_settings_update(self, app_name: str,settings:GoogleAuthCredentials=Body()) -> str:
        # code="4/0AeaYSHB7RHy_Chta27XKeYlvTL_R8AU4JaAlqT1nISgyRHJBxdoH4k5QsShnMUwRc4pcTQ"
        code = self.request.query_params.get("code")
        access_token_key= self.g_drive_service.get_access_token(code=code)

        return code




