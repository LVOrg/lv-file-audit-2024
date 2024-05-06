import json
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
class MSAuth(BaseController):
    @controller.router.get(
        path="/api/{app_name}/after-ms-login"
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

