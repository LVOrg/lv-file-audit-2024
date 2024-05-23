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
        "/api/{app_name}/after-google-login", summary="after login to google",
        tags = ["CLOUD-GOOGLE"]
    )
    def after_login_google(self, app_name: str) :
        hrml=("<p>Here are some security tips to keep your account safe:</p>"
              "<ul>"
              " <li>Never share your login credentials with anyone.</li>"
              "<li>Be cautious of suspicious emails or websites asking for your Google login.</li>"
              "<li>Consider enabling two-factor authentication for your Google account for an extra layer of security.</li>"
              "</ul>"
              )
        code = self.request.query_params.get("code")
        if not self.request.query_params or not code:
            error_html = ("<p>It looks like you call this page without google consent login. The page will automatically "
                    "summon after google consent login. </p>"
                    "<ul>"
                    f" <li>After do prover settings in tenant '{app_name}' </li>"
                    "<li>Update the codx app will automatically redirect to this pag</li>"
                    "</ul>"
                    )
            html_content = (f"<html>"
                            f"  <body>"
                            f"{error_html}"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        client_id,client_secret,_,error = self.g_drive_service.get_id_and_secret(app_name)
        if isinstance(error,dict):
            error_html=(f"<p>"
                        f"<label>Error&nbsp;:</label><b>{error.get('Code')}</b>"
                        f"{error.get('Message')}"
                        f"</p>")
            html_content = (f"<html>"
                            f"  <body>"
                            f"{error_html}"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
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
            access_token= access_token_key.get("access_token")
            expires_in=access_token_key.get("expires_in")
            scope = access_token_key.get("scope")
            token_type= access_token_key.get("token_type")
            self.g_drive_service.save_refresh_access_token(
                app_name = app_name,
                refresh_token = refresh_token,
                access_token = access_token,
                expires_in = expires_in,
                scope = scope,
                token_type =token_type
            )
            html_content = (f"<html>"
                            f"  <body>"
                            f"{hrml}"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        else:
            return "Error"

        return code

    @controller.route.post(
        "/api/{app_name}/cloud/google/get-google-redirect-uri",
        tags=["CLOUD-GOOGLE"]
    )
    def get_google_after_login_url(self,app_name):
        url = self.g_drive_service.get_redirect_uri(
            request=self.request,
            app_name=app_name
        )
        return url

    @controller.route.post(
        "/api/{app_name}/cloud/google/get-login-url",
        tags = ["CLOUD-GOOGLE"]
    )
    def cloud_google_get_login_url(self,
                                   app_name:str,
                                   scopes:typing.List[str]=Body(embed=True)):
        """
        Get url of Google consent login </br>
        Nhận url đăng nhập đồng ý của Google </br>
        scopes: example "gmail.send","drive" see in https://console.cloud.google.com/ </br>
        :return:
        """
        # client_id, client_secret = self.g_drive_service.get_id_and_secret(app_name)
        url,error= self.g_drive_service.get_login_url(
            request= self.request,
            app_name=app_name,
            scopes=scopes
        )
        if error:
            return dict(
                Error=error
            )
        else:
            return dict(
                Data=url
            )
        # response = Response()
        # response.status_code = 302
        # response.headers["Location"] = url
        # return response


