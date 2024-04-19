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


@controller.resource()
class GoogleController(BaseController):
    # dependencies = [
    #     Depends(Authenticate)
    # ]

    def __init__(self, request: Request):
        self.request = request

    @controller.route.get(
        "/api/{app_name}/after-google-login", summary="after login to google"
    )
    def after_login_google(self, app_name: str) -> str:
        # code="4/0AeaYSHB7RHy_Chta27XKeYlvTL_R8AU4JaAlqT1nISgyRHJBxdoH4k5QsShnMUwRc4pcTQ"
        code = self.request.query_params.get("code")
        access_token_key= self.g_drive_service.get_access_token(
            code=code,
            client_id="437264324741-r6ppgq59tcu264tufv0sbba014mrtc68.apps.googleusercontent.com",
            client_secret="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"
        )

        return code

    @controller.route.get(
        "/api/{app_name}/google-login", summary="after login to google"
    )
    def login(self,app_name:str):
        """

        :return:
        """

        url= self.g_drive_service.get_login_url(
            request= self.request,
            app_name=app_name,
            client_id ="437264324741-r6ppgq59tcu264tufv0sbba014mrtc68.apps.googleusercontent.com"
        )
        response = Response()
        response.status_code = 302
        response.headers["Location"] = url
        return response


