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
from google.oauth2 import service_account
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
    def after_login_google(self, app_name: str) :

        code = self.request.query_params.get("code")
        client_id,client_secret = self.g_drive_service.get_id_and_secret(app_name)
        redirect_uri = self.g_drive_service.get_redirect_uri(app_name)
        if client_id and client_secret:
            access_token_key= self.g_drive_service.get_access_token(
                code=code,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
            )
            #google.auth.exceptions.RefreshError: The credentials do not contain the necessary fields need to refresh the access token.
            # You must specify
            # refresh_token,
            # token_uri,
            # client_id,
            # and client_secret.

            refresh_token= access_token_key.get("refresh_token")
            self.g_drive_service.save_refresh_access_token(
                app_name = app_name,
                refresh_token = refresh_token
            )
            return access_token_key
        else:
            return "Error"

        return code

    @controller.route.get(
        "/api/{app_name}/google-login", summary="after login to google"
    )
    def login(self,app_name:str):
        """

        :return:
        """
        client_id, client_secret = self.g_drive_service.get_id_and_secret(app_name)
        url= self.g_drive_service.get_login_url(
            request= self.request,
            app_name=app_name
        )
        response = Response()
        response.status_code = 302
        response.headers["Location"] = url
        return response


