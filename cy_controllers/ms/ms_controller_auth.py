import json

from fastapi_router_controller import Controller

from fastapi import (
    APIRouter,
    Response,

)
from cy_controllers.common.base_controller import BaseController
router = APIRouter()
controller = Controller(router)



@controller.resource()
class MSAuth(BaseController):
    @controller.router.get(
        path="/api/{app_name}/cloud/azure/get-login-url"
    )
    async def one_drive_folder_list(self, app_name: str):
        query = self.request.query_params or {}
        if query.get('error'):
            html_content = (f"<html>"
                            f"  <body>"
                            f"      <p><label>Error &nbsp:</label><span>{query.get('error')}</span></p>"
                            f"      <p><label>Error Description &nbsp:</label><span>{query.get('error_description')}</span></p>"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        code = query["code"]
        access_token, refresh_token,id_token,scope,expire_in,error = self.ms_common_service.get_token_from_app_by_verify_code(
            app_name=app_name,
            verify_code=code
        )
        if not  error:
            self.ms_common_service.authenticate_update(
                app_name=app_name,
                access_token =access_token,
                refresh_token = refresh_token,
                id_token = id_token,
                utc_expire = expire_in,
                scope = scope
            )
            html_content = (f"<html>"
                            f"  <body>"
                            f"      <p><b>User's explicit consent</b></p>"
                            f"MS consent is a critical security measure that protects user privacy by ensuring they have "
                            f"control over what data your application can access. Understanding how MS consent works is "
                            f"essential for developing secure and user-friendly applications that leverage delegated "
                            f"permissions in the Microsoft identity platform."
                            f"<p>Thank you for granting consent! We appreciate your trust in allowing us to access your data.</p>"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        else:
            return Response(content=json.dumps(error), media_type="application/json")
            # url, error = self.ms_common_service.get_url(app_name=app_name, scopes=scopes)

    @controller.router.get(
        path="/api/{app_name}/after-ms-login"
    )
    def after_ms_login(self,app_name:str):
        if self.request.query_params.get("error"):
            error_html = (f"<p>"
                          f"<label>Error&nbsp;:</label><b>{self.request.query_params.get('error')}</b></br>"
                          f"{self.request.query_params.get('error_description')}"
                          f"</p>")
            html_content = (f"<html>"
                            f"  <body>"
                            f"{error_html}"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        code = self.request.query_params.get("code")
        # tenant_id,client_id,client_secret,redirect_url = self.ms_common_service.settings_get(app_name)
        # token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        auth_info,error = self.ms_common_service.get_token_from_app_by_verify_code(app_name,code)
        if error:
            error_html = (f"<p>"
                          f"<label>Error&nbsp;:</label><b>{error.get('Code')}</b></br>"
                          f"{error.get('Message')}"
                          f"</p>")
            html_content = (f"<html>"
                            f"  <body>"
                            f"{error_html}"
                            f"  </body>"
                            f"</html>")
            return Response(content=html_content, media_type="text/html")
        # Data for the token request

        self.ms_common_service.authenticate_update(
            app_name=app_name,
            access_token=auth_info.access_token,
            refresh_token=auth_info.refresh_token,
            id_token=auth_info.id_token,
            scope=auth_info.scope,
            utc_expire=auth_info.expire_on

        )

        msg_content= (f'<!DOCTYPE html><html lang="en">'
                      f'<head>'
                      f'    <meta charset="UTF-8">'
                      f'    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
                      f'    <title>Microsoft Azure Consent Successful</title>'
                      f'</head>'
                      f'<body>'
                      f'    <h1>Microsoft Azure Consent Successful</h1>'
                      f'    <p>You have successfully granted the necessary permissions for your account. You can now close this browser window.</p>'
                      f'    <p><b>Thank you!</b></p></html>')


        return Response(content=msg_content, media_type="text/html")