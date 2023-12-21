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
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException, call_ms_func
from cy_fucking_whore_microsoft import auth
from cy_fucking_whore_microsoft.fucking_models.verify_access_token_result import (
    GetUserInfoResult, UserInfo, BullShitError
)
from cy_fucking_whore_microsoft.fucking_models.new_token_result import (
    AcquireNewToken, AcquireNewTokenResult
)
from cy_fucking_whore_microsoft.fwcking_auth import urls_auth, scopes

from cy_fucking_whore_microsoft.fucking_models.get_scope_result import (
    ScopeInfo, ScopesInfoResult
)
from cy_fucking_whore_microsoft.fucking_models.get_token import GetTokenResult
from cy_fucking_whore_microsoft.fucking_models.accounts import (
    InviteUserResult
)
from cy_xdoc.auths import Authenticate
@controller.resource()
class AzureController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.route.get(
        "/api/{app_name}/azure/after_login",
        summary="After login to Azure is OK. Use this api to get the f**king Access Token Key"
    )
    async def after_login(self, app_name: str) -> typing.Optional[typing.Any]:

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
        qr = self.service_app.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower==app_name.lower()
        )

        UrlLogin = None

        if app[qr.fields.AppOnCloud.Azure] is not None:
            try:
                access_token = auth.get_auth_token(
                    verify_code=verify_code,
                    redirect_uri= self.fucking_azure_account_service.get_handler_after_login_url(app_name),
                    tenant=app[qr.fields.AppOnCloud.Azure.TenantId],
                    client_id=app[qr.fields.AppOnCloud.Azure.ClientId],
                    client_secret=app[qr.fields.AppOnCloud.Azure.ClientSecret],
                    is_business_account= not app[qr.fields.AppOnCloud.Azure.IsPersonal]


                )
                _access_token = None
                _refresh_token = None
                _id_token = None
                if hasattr(access_token, "access_token"):
                    _access_token = access_token.access_token
                if hasattr(access_token, "refresh_token"):
                    _refresh_token = access_token.refresh_token
                if hasattr(access_token, "id_token"):
                    _id_token = access_token.id_token
                self.service_app.save_azure_access_token(
                    app_name=app_name,
                    azure_access_token=_access_token,
                    azure_refresh_token=_refresh_token,
                    azure_token_id=_id_token,
                    azure_verify_code=verify_code
                )
                self.fucking_azure_account_service.clear_token_cache(
                    app_name=app_name
                )
                self.fucking_azure_onedrive_service.clear_cache(
                    app_name=app_name
                )

                # return app.to_pydantic()
                from fastapi.responses import HTMLResponse
                ret = f"<html><head></head><body><span>Access Token</span><br/><textarea style='width:100%;min-height:300px'>{_access_token}</textarea></body></html>"
                ret += f"<html><head></head><body><span>Token ID</span><br/><textarea style='width:100%;min-height:300px'>{_id_token}</textarea></body></html>"
                return HTMLResponse(f"<html>"
                                    f"<head>"
                                    f"</head>"
                                    f"<body>"
                                    f"Now, You can close your browser."
                                    f"</body>"
                                    f"</html>")
            except FuckingWhoreMSApiCallException as e:
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=500,
                    content=dict(
                        code=e.code,
                        message=e.message
                    )
                )


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
        c = ""
        for key, value in form_data.items():
            c += f"{key}={value}"
            print(f"Key: {key}, Value: {value}")
        ret = f"<html><head></head><body><textarea style='width:100%;min-height:300px'>{form_data['id_token']}</textarea></body></html>"
        return HTMLResponse(ret)

    @controller.router.post(
        path="/api/{app_name}/azure/verify_access_token"
    )
    async def verify_access_token(self, app_name: str, access_token: str = Body(embed=True)) -> GetUserInfoResult:
        ret = GetUserInfoResult()
        try:
            ret_info = self.fucking_azure_account_service.get_current_acc_info(
                access_token=access_token
            )
            ret.user = UserInfo(**ret_info)
            return ret
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(**e.__dict__)
            return ret
    @controller.router.post(
        path="/api/{app_name}/azure/acquire_new_token"
    )
    async def refresh_token(self,app_name:str,refresh_token: str = Body(embed=True))->AcquireNewTokenResult:
        ret= AcquireNewTokenResult()

        try:
            ret_info = self.fucking_azure_account_service.acquire_new_token(
                refresh_token = refresh_token
            )
            ret.user = UserInfo(**ret_info)
            return ret
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(**e.__dict__)
            return ret
    @controller.router.post(
        path="/api/{app_name}/azure/get_scope"
    )
    async def get_scope(self,app_name:str)->ScopesInfoResult:
        ret = ScopesInfoResult()
        qr = self.service_app.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower==app_name.lower()
        )
        if app is None:
            app = qr.context.find_one(
                qr.fields.Name == app_name
            )
            if app:
                qr.context.update(
                    qr.fields.Name == app_name,
                    qr.fields.NameLower << app_name.lower()
                )
        if app is None:
            ret.error = BullShitError(
                code="AppWasNotFound",
                message=f"Application {app_name} was not found in LV File Service"
            )
            return ret

        fucking_azure_app = app[qr.fields.AppOnCloud.Azure]
        if fucking_azure_app is None:
            ret.error = BullShitError(
                code="AppAzureWasNotLink",
                message=f"We could not find any link information to Azure. "
                        f"Please! config your application in LV File Service"
            )
            return ret
        fucking_azure_client_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]

        try:
            token2 = urls_auth.accquire_access_token_key_token(
                client_id=fucking_azure_client_id,
                tenant_id=fucking_azure_tenant_id,
                secret_value=fucking_azure_client_secret

            )
            import jwt
            decoded_token = jwt.decode(token2, options={"verify_signature": False, "verify_aud": False})
            roles = decoded_token.get("roles",[])
            scope_ret = [ ScopeInfo(name=x, description="") for  x in roles]

            ret.scopes = scope_ret

            return ret
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(
                code= e.code,
                message = e.message
            )
            return ret
    @controller.router.post(
        path="/api/{app_name}/azure/get_token"
    )
    async def get_token(self,app_name:str)->GetTokenResult:
        qr = self.service_app.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower==app_name.lower()
        )
        ret = GetTokenResult()
        if app is None:
            ret.error = BullShitError(
                code="MissMSLink",
                message=f"Application {app_name} was not link to MS live"
            )
            return ret
        client_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        refresh_token = app[qr.fields.AppOnCloud.Azure.RefreshToken]
        if client_id is None or tenant_id is None or client_secret is None or refresh_token is None:
            ret.error = BullShitError(
                code="MissMSLink",
                message=f"Application {app_name} was not link to MS live or never login to MS Live before"
            )
            return ret
        try:
            ret_info = self.fucking_azure_account_service.acquire_new_token(
                app_name = app_name,
                refresh_token = refresh_token,
                scope = []
            )
            scopes = ret_info.get("scope","").split(' ')
            ret.scopes = scopes
            ret.token = ret_info["access_token"]
            return ret
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(**e.__dict__)
            return ret

    @controller.router.post(
        path="/api/{app_name}/azure/invite_user"
    )
    async def invite_user(self,app_name:str, email:str = Body(embed=True),display_name:str = Body(embed=True))->InviteUserResult:
        ret = InviteUserResult()
        try:
            token = self.fucking_azure_account_service.acquire_token(
                app_name
            )
            ret_data = call_ms_func(
                method="post",
                api_url="invitations",
                token = token,
                body= dict(
                    invitedUserEmailAddress = email,
                    invitedUserDisplayName = display_name,
                    sendInvitation = True
                ),
                return_type=dict,
                request_content_type="application/json"
            )

            ret.data = ret_data
            return ret

        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(
                code = e.code,
                message = e.message
            )
            return ret

    @controller.router.get(
        path="/api/{app_name}/azure/invite_acceptance"
    )
    async def invite_acceptance(self,app_name):
        return "OK"

    @controller.router.post(
        path="/api/{app_name}/azure/get_login_url"
    )
    async def get_login_url(self,app_name:str)->typing.Union[str,dict]:
        try:
            ret =self.fucking_azure_account_service.get_login_url(app_name)
            return dict(
                loginUrl=ret
            )
        except FuckingWhoreMSApiCallException as e:
            return dict(
                error=dict(
                    code=e.code,
                    message=e.message
                )
            )

    @controller.router.post(
        path="/api/{app_name}/azure/get_login_url_with_business_account"
    )
    async def get_login_url(self, app_name: str) -> typing.Union[str, dict]:
        try:
            ret = self.fucking_azure_account_service.get_login_url(app_name,is_business_account=True)
            return dict(
                loginUrl=ret
            )
        except FuckingWhoreMSApiCallException as e:
            return dict(
                error=dict(
                    code=e.code,
                    message=e.message
                )
            )