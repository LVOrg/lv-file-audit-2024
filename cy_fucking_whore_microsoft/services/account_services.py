import json
import typing

import cy_kit
from cy_fucking_whore_microsoft.fwcking_ms.caller import call_ms_func, FuckingWhoreMSApiCallException
import jwt
import requests
from cy_xdoc.services.apps import AppServices
from enum import Enum


class AccountService:
    def __init__(self, app_service = cy_kit.singleton(AppServices) ):
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

    def acquire_new_token(self,app_name:str, refresh_token:str, scope: typing.List[str])->dict:

        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower==app_name.lower()
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
            data= dict(
                grant_type = "refresh_token",
                refresh_token = refresh_token,
                client_id = fucking_ms_app_azure_id,
                scope = scope,
                client_secret =fucking_ms_app_azure_client_secret

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
                message= f"It looks like app in MS live does not meet requirement", code="AcquireFail"
            )
            raise ex
        decoded_token = jwt.decode(data.get("id_token"), options={"verify_signature": False, "verify_aud": False})
        if decoded_token.get('aud')!=fucking_ms_app_azure_id:
            ex = FuckingWhoreMSApiCallException(
                message=f"Application {app_name} in LV File Service link to {decoded_token.get('aud')}, not link to {fucking_ms_app_azure_id}",
                code="AcquireFail"
            )
            raise ex
        if data.get("refresh_token"):
            qr.context.update(
                qr.fields.NameLower==app_name.lower(),
                qr.fields.AppOnCloud.Azure.RefreshToken<< data.get("refresh_token")
            )
        return data

    def acquire_token(self,app_name:str)->str:
        """
        This fucking function server for fucking Microsoft Azure Service such as : One drive Office  365.
        Before call this function.
        make sure the fucking that: The application embody by app_name ready link to fucking Microsoft
        :param app_name:
        :return:
        """
        qr = self.app_service.get_queryable()
        app = qr.context.find_one(
            qr.fields.NameLower==app_name.lower()
        )
        if app is None:
            raise FuckingWhoreMSApiCallException(
                code="AppNotFound",
                message=f"Application {app_name} is not link to MS"
            )

        fucking_ms_app_azure_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        fucking_ms_app_azure_is_personal = app[qr.fields.AppOnCloud.Azure.IsPersonal] or False
        fucking_ms_app_azure_tenant_id = app[qr.fields.AppOnCloud.Azure.TenantId]
        fucking_ms_app_azure_reresh_token = app[qr.fields.AppOnCloud.Azure.RefreshToken]
        fucking_ms_app_azure_client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        if (fucking_ms_app_azure_reresh_token is None
                or fucking_ms_app_azure_tenant_id is None
                or fucking_ms_app_azure_id is None
                or fucking_ms_app_azure_client_secret is None):
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
                refresh_token=fucking_ms_app_azure_reresh_token,
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
                code="AcquireFail"
            )
            raise ex
        if data.get("access_token") is None:
            ex = FuckingWhoreMSApiCallException(
                message=f"Application {app_name} in LV File Service link to {decoded_token.get('aud')}, not link to {fucking_ms_app_azure_id}",
                code="AcquireFail"
            )
            raise ex
        return data["access_token"]
        





