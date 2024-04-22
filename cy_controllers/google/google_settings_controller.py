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
  ClientId: str
  ClientSecret: str
from fastapi import Body
from cyx.repository import Repository
@controller.resource()
class GoogleSettingsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        self.request = request

    @controller.route.post(
        "/api/{app_name}/google-drive-settings/update", summary="Update settings for google drive"
    )
    def google_drive_settings_update(self, app_name: str,settings:GoogleAuthCredentials=Body()):
        try:
            Repository.apps.app('admin').context.update(
                Repository.apps.fields.Name==app_name,
                Repository.apps.fields.AppOnCloud.Google.ClientId<<settings.ClientId,
                Repository.apps.fields.AppOnCloud.Google.ClientSecret << settings.ClientSecret
            )
            return dict(
                ok=True
            )
        except Exception as ex:
            return dict(
                error=dict(
                    code="system",
                    desccription=ex.__str__()
                )
            )

    @controller.route.post(
        "/api/{app_name}/google-drive-settings/get", summary="Update settings for google drive"
    )
    def google_drive_settings_get(self, app_name: str):
        ret = Repository.apps.app('admin').context.aggregate().match(
            Repository.apps.fields.Name==app_name
        ).project(
            cy_docs.fields.ClientId>>Repository.apps.fields.AppOnCloud.Google.ClientId,
            cy_docs.fields.ClientSecret>>Repository.apps.fields.AppOnCloud.Google.ClientSecret
        )
        ret=list(ret)
        if len(ret)>0:
            return ret[0]
        return None

