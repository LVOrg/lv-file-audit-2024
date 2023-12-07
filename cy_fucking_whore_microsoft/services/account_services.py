import json
import typing
import uuid

import cy_kit
from cy_fucking_whore_microsoft.fwcking_ms.caller import call_ms_func, FuckingWhoreMSApiCallException, ErrorEnum
import jwt
import requests
from cy_xdoc.services.apps import AppServices
from enum import Enum


class AccountService:
    def __init__(self, app_service=cy_kit.singleton(AppServices)):
        self.app_service = app_service

    def get_current_acc_info(self, access_token) -> dict:
        """
        The shit function use for current account info getting from Whore-Microsoft-Online
        :param access_token:
        :return:
        """
        return call_ms_func(
            api_url="me",
            token=access_token,
            body=None,
            method="get",
            request_content_type=None,
            return_type=dict
        )

    def acquire_acc_info(self, app_name: str) -> dict:
        """
        The shit function use for current account info getting from Whore-Microsoft-Online
        :param access_token:
        :return:
        """
        token = self.acquire_token(app_name)
        return call_ms_func(
            api_url="me",
            token=token,
            body=None,
            method="get",
            request_content_type=None,
            return_type=dict
        )

    def acquire_new_token(self, app_name: str, refresh_token: str, scope: typing.List[str]) -> dict:

        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower == app_name.lower()
        )

        fucking_ms_app_azure_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_ms_app_azure_is_personal = app[qr.fields.AppOnCloud.Azure.IsPersonal] or False
        fucking_ms_app_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_ms_app_azure_reresh_token = app[qr.fields.AppOnCloud.Azure.RefreshToken]
        fucking_ms_app_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        if fucking_ms_app_azure_reresh_token is None:
            raise FuckingWhoreMSApiCallException(
                message=f"It looks like Application {app_name} never login before, could you please login to MS live at front end!",
                code="RequireFrontEndLogin"
            )
        post_url = f"https://login.microsoftonline.com/{fucking_ms_app_azure_tenant_id}/oauth2/v2.0/token"
        if fucking_ms_app_azure_is_personal:
            post_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        res = requests.post(
            url=post_url,
            data=dict(
                grant_type="refresh_token",
                refresh_token=refresh_token,
                client_id=fucking_ms_app_azure_id,
                scope=scope,
                client_secret=fucking_ms_app_azure_client_secret

            )
        )
        data = json.loads(res.text)
        if data.get("error"):
            error_dict = data.get("error")
            error_message = error_dict.get("message")
            error_code = error_dict.get("code")
            ex = FuckingWhoreMSApiCallException(message=error_message, code=error_code)
            raise ex
        if data.get("id_token") is None:
            ex = FuckingWhoreMSApiCallException(
                message=f"It looks like app in MS live does not meet requirement", code="AcquireFail"
            )
            raise ex
        decoded_token = jwt.decode(data.get("id_token"), options={"verify_signature": False, "verify_aud": False})
        if decoded_token.get('aud') != fucking_ms_app_azure_id:
            ex = FuckingWhoreMSApiCallException(
                message=f"Application {app_name} in LV File Service link to {decoded_token.get('aud')}, not link to {fucking_ms_app_azure_id}",
                code="AcquireFail"
            )
            raise ex
        if data.get("refresh_token"):
            qr.context.update(
                qr.fields.NameLower == app_name.lower(),
                qr.fields.AppOnCloud.Azure.RefreshToken << data.get("refresh_token")
            )
        return data

    def acquire_token(self, app_name: str) -> str:
        """
        This fucking function server for fucking Microsoft Azure Service such as : One drive Office  365.
        Before call this function.
        make sure the fucking that: The application embody by app_name ready link to fucking Microsoft
        :param app_name:
        :return:
        """
        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower == app_name.lower()
        )

        if app is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.APP_NOT_FOUND,
                message=f"Application {app_name} is not link to MS"
            )
        if app[qr.fields.AppOnCloud] is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.REQUIRE_LINK_TO_MICROSOFT,
                message=f"Application {app_name} is not link to MS"
            )
        fucking_ms_app_azure_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_ms_app_azure_is_personal = app[qr.fields.AppOnCloud.Azure.IsPersonal] or False
        fucking_ms_app_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_ms_app_azure_refresh_token = app[qr.fields.AppOnCloud.Azure.RefreshToken]
        fucking_ms_app_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        if (fucking_ms_app_azure_refresh_token is None
                or fucking_ms_app_azure_tenant_id is None
                or fucking_ms_app_azure_id is None
                or fucking_ms_app_azure_client_secret is None):
            raise FuckingWhoreMSApiCallException(
                message=f"It looks like Application {app_name} never login to MS live "
                        f"before, could you please login to MS live at front end!",
                code=ErrorEnum.REQUIRE_LOGIN_TO_MICROSOFT
            )
        fucking_ms_onedrive_dir = app[qr.fields.AppOnCloud.Azure.RootDir]
        if fucking_ms_onedrive_dir is None:
            fucking_ms_onedrive_dir = str(uuid.uuid4())
            qr.context.update(
                qr.fields.NameLower == app_name.lower(),
                qr.fields.AppOnCloud.Azure.RootDir << fucking_ms_app_azure_id

            )
        post_url = f"https://login.microsoftonline.com/{fucking_ms_app_azure_tenant_id}/oauth2/v2.0/token"
        if fucking_ms_app_azure_is_personal:
            post_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        res = requests.post(
            url=post_url,
            data=dict(
                grant_type="refresh_token",
                refresh_token=fucking_ms_app_azure_refresh_token,
                client_id=fucking_ms_app_azure_id,
                scope=[],
                client_secret=fucking_ms_app_azure_client_secret

            )
        )

        data = json.loads(res.text)
        if data.get("error"):
            error_dict = data.get("error")
            error_message = error_dict.get("message")
            error_code = error_dict.get("code")
            ex = FuckingWhoreMSApiCallException(message=error_message, code=error_code)
            raise ex
        if data.get("id_token") is None:
            ex = FuckingWhoreMSApiCallException(
                message=f"It looks like app in MS live does not meet requirement", code="AcquireFail"
            )
            raise ex
        decoded_token = jwt.decode(data.get("id_token"), options={"verify_signature": False, "verify_aud": False})
        if decoded_token.get('aud') != fucking_ms_app_azure_id:
            ex = FuckingWhoreMSApiCallException(
                message=f"Application {app_name} in LV File Service link to {decoded_token.get('aud')}, not link to {fucking_ms_app_azure_id}",
                code=ErrorEnum.IMPROPER_MICROSOFT_APP_REGISTER
            )
            raise ex
        if data.get("access_token") is None:
            ex = FuckingWhoreMSApiCallException(
                message=f"Application {app_name} in LV File Service link to {decoded_token.get('aud')}, not link to {fucking_ms_app_azure_id}",
                code=ErrorEnum.IMPROPER_MICROSOFT_APP_REGISTER
            )
            raise ex
        return data["access_token"]

    def get_root_dir_of_one_drive(self, app_name) -> str:
        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower == app_name.lower()
        )

        if app is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.APP_NOT_FOUND,
                message=f"Application {app_name} is not link to MS"
            )
        if app[qr.fields.AppOnCloud] is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.REQUIRE_LINK_TO_MICROSOFT,
                message=f"Application {app_name} is not link to MS"
            )
        fucking_ms_app_azure_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_ms_app_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_ms_app_azure_reresh_token = app[qr.fields.AppOnCloud.Azure.RefreshToken]
        fucking_ms_app_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        if (fucking_ms_app_azure_reresh_token is None
                or fucking_ms_app_azure_tenant_id is None
                or fucking_ms_app_azure_id is None
                or fucking_ms_app_azure_client_secret is None):
            raise FuckingWhoreMSApiCallException(
                message=f"It looks like Application {app_name} never login to MS live "
                        f"before, could you please login to MS live at front end!",
                code=ErrorEnum.REQUIRE_LOGIN_TO_MICROSOFT
            )
        fucking_ms_onedrive_dir = app[qr.fields.AppOnCloud.Azure.RootDir]
        if fucking_ms_onedrive_dir is None:
            fucking_ms_onedrive_dir = str(uuid.uuid4())
            qr.context.update(
                qr.fields.NameLower == app_name.lower(),
                qr.fields.AppOnCloud.Azure.RootDir << fucking_ms_app_azure_id

            )
        return fucking_ms_onedrive_dir

    def get_handler_after_login_url(self, app_name: str):
        import cy_web
        return f"{cy_web.get_host_url()}/api/{app_name}/azure/after_login"

    def get_login_url(self, app_name):
        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower == app_name.lower()
        )

        if app is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.APP_NOT_FOUND,
                message=f"Application {app_name} was not found in LV File Service"
            )
        fucking_ms_app_azure_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_ms_app_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_ms_app_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        fucking_ms_app_azure_is_personal = app[qr.fields.AppOnCloud.Azure.IsPersonal]
        if None in [
            fucking_ms_app_azure_id,
            fucking_ms_app_azure_tenant_id,
            fucking_ms_app_azure_client_secret
        ]:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.REQUIRE_LINK_TO_MICROSOFT,
                message=f"Application {app_name} is not link to MS"
            )

        from cy_fucking_whore_microsoft.fwcking_auth import urls_auth, scopes
        import cy_web
        # https://f297-115-79-200-101.ngrok-free.app/api/lv-docs/azure/after_login
        if fucking_ms_app_azure_is_personal:
            return urls_auth.get_personal_account_login_url(
                client_id=fucking_ms_app_azure_id,
                scopes=scopes.get_one_drive() + scopes.get_account(),
                redirect_uri=self.get_handler_after_login_url(app_name)
            )
        else:
            return urls_auth.get_business_account_login_url(
                client_id=fucking_ms_app_azure_id,
                scopes=scopes.get_one_drive() + scopes.get_account(),
                redirect_uri=self.get_handler_after_login_url(app_name)
            )
