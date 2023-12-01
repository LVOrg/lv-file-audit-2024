import typing

from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

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
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
import urllib


@controller.resource()
class AzureController(BaseController):

    @controller.route.get(
        "/api/{app_name}/azure/after_login",
        summary="After login to Azure is OK. Use this api to get the f**king Access Token Key"
    )
    async def after_login(self, app_name: str) -> typing.Optional[typing.Any]:
        from cy_azure import auth
        if self.request.query_params.get("error"):
            return self.request.query_params.get("error_description")
        verify_code = auth.get_verify_code(self.request)
        redirect_uri = str(self.request.url).split('?')[0]
        """
        If everything from Whore-Microsoft-Azure:
        The will get the shit verify code, then get Access Token
        """
        if self.request.query_params.get("id_token"):
            _access_token = self.request.query_params.get("id_token")
            from fastapi.responses import HTMLResponse
            ret = f"<html><head></head><body><textarea style='width:100%;min-height:300px'>{_access_token}</textarea></body></html>"
            return HTMLResponse(ret)
        app = self.service_app.get_item(
            app_name='admin',
            app_get=app_name
        )
        UrlLogin = None
        if (app.Apps and
                app.Apps.get("Azure") and
                isinstance(app.Apps["Azure"], dict) and
                app.Apps["Azure"].get("UrlLogin") and
                isinstance(app.Apps["Azure"]["UrlLogin"], str)):
            UrlLogin = app.Apps["Azure"]["UrlLogin"]
            uri_login = urllib.parse.urlparse(UrlLogin)
            t_data = dict(
                [[x.split('=')[0], urllib.parse.unquote(x.split('=')[1])] for x in uri_login.query.split('&') if
                 "=" in x])
            UrlLogin = t_data["redirect_uri"]
            if UrlLogin != redirect_uri:
                raise Exception("Invalid request or Azure App register")
            if (not app.Apps["Azure"].get("ClientId") or
                    not app.Apps["Azure"].get("TenantId") or
                    not app.Apps["Azure"].get("ClientSecret")):
                raise Exception("Invalid request or Azure App register")
            try:
                access_token = auth.get_auth_token(
                    verify_code=verify_code,
                    redirect_uri=UrlLogin,
                    tenant=  app.Apps["Azure"].get("TenantId"),
                    client_id=app.Apps["Azure"].get("ClientId"),
                    client_secret= app.Apps["Azure"].get("ClientSecret")

                )
                _access_token= None
                _refresh_token= None
                _id_token= None
                if hasattr(access_token,"access_token"):
                    _access_token = access_token.access_token
                if hasattr(access_token,"refresh_token"):
                    _refresh_token = access_token.refresh_token
                if hasattr(access_token,"id_token"):
                    _id_token = access_token.id_token
                self.service_app.save_azure_access_token(
                    app_name=app_name,
                    azure_access_token = _access_token,
                    azure_refresh_token= _refresh_token,
                    azure_token_id= _id_token
                )

                # return app.to_pydantic()
                from fastapi.responses import HTMLResponse
                ret=f"<html><head></head><body><span>Access Token</span><br/><textarea style='width:100%;min-height:300px'>{_access_token}</textarea></body></html>"
                ret += f"<html><head></head><body><span>Token ID</span><br/><textarea style='width:100%;min-height:300px'>{_id_token}</textarea></body></html>"
                return HTMLResponse(ret)

            except Exception as e:
                import traceback
                ret_error = traceback.format_exception(e)
                return ret_error
        else:
            raise Exception(f"{app_name} was not link to Microsoft Azure App")

    @controller.route.post(
        "/api/{app_name}/azure/after_login",
        summary="After login to Azure is OK. Use this api to get the f**king Access Token Key"
    )
    async def after_login(self, app_name: str):
        from fastapi.responses import HTMLResponse
        form_data = await self.request.form()
        c=""
        for key, value in form_data.items():
            c+=f"{key}={value}"
            print(f"Key: {key}, Value: {value}")
        ret = f"<html><head></head><body><textarea style='width:100%;min-height:300px'>{form_data['id_token']}</textarea></body></html>"
        return HTMLResponse(ret)
