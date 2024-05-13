import datetime
import json
import typing

import requests

import cy_docs
import cy_kit
from cyx.repository import Repository
from msgraph import GraphServiceClient
from azure.identity.aio import ClientSecretCredential
from cyx.cloud.azure.azure_utils import call_ms_func


class AzureInfo:
    tenant_id: str
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: str
    scope: str


class AccquireTokenInfo:
    token_type: str
    scope: str
    expires_in: str
    ext_expires_in: str
    access_token: str
    id_token: str
    expires_on: datetime.datetime


from cyx.cache_service.memcache_service import MemcacheServices


class AzureUtilsServices:
    def __init__(self, mem_cache_services: MemcacheServices = cy_kit.singleton(MemcacheServices)):
        self.cache_key = f"{type(self).__module__}/{type(self).__name__}/v1"
        self.mem_cache_services = mem_cache_services

    def get_credential(self, app_name: str) -> typing.Tuple[ClientSecretCredential | None, dict | None]:
        azure_info, error = self.get_azure_info(app_name)
        if error:
            return None, error

        credential = ClientSecretCredential(azure_info.tenant_id,
                                            azure_info.client_id,
                                            azure_info.client_secret)
        return credential, None

    def acquire_token(self, app_name) -> typing.Tuple[AccquireTokenInfo | None, dict | None]:
        key = f"{self.cache_key}/{app_name}/token"
        ret = self.mem_cache_services.get_object(key, AccquireTokenInfo)
        if ret is not None and (datetime.datetime.utcnow() - ret.expires_on).total_seconds() > 5:
            return ret, None

        azure_info, error = self.get_azure_info(app_name)
        # post_url = f"https://login.microsoftonline.com/{fucking_ms_app_azure_tenant_id}/oauth2/v2.0/token"
        # if fucking_ms_app_azure_is_personal:
        post_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        res = requests.post(
            url=post_url,
            data=dict(
                grant_type="refresh_token",
                refresh_token=azure_info.refresh_token,
                client_id=azure_info.client_id,
                scope=azure_info.scope.split(' '),
                client_secret=azure_info.client_secret

            )
        )

        data = json.loads(res.text)
        if data.get("error"):
            return None, dict(Code=data.get("error"), Message=data.get("error_description"))
        else:
            ret = AccquireTokenInfo()
            for k, v in data.items():
                setattr(ret, k, v)
            ret.expires_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(ret.expires_in))
            self.mem_cache_services.set_object(key, ret)
            return ret, None

    def get_azure_info(self, app_name) -> typing.Tuple[AzureInfo | None, dict | None]:
        """
        Get all info has been setup for app
        :param app_name:
        :return: azure_info, error
        """
        data = self.mem_cache_services.get_object(f"{self.cache_key}/{app_name}", AzureInfo)
        if data:
            return data, None
        else:
            app_context = Repository.apps.app("admin").context
            data = app_context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.client_id >> Repository.apps.fields.AppOnCloud.Azure.ClientId,
                cy_docs.fields.client_secret >> Repository.apps.fields.AppOnCloud.Azure.ClientSecret,
                cy_docs.fields.tenant_id >> Repository.apps.fields.AppOnCloud.Azure.TenantId,
                cy_docs.fields.access_token >> Repository.apps.fields.AppOnCloud.Azure.AccessToken,
                cy_docs.fields.scope >> Repository.apps.fields.AppOnCloud.Azure.Scope,
                cy_docs.fields.refresh_token >> Repository.apps.fields.AppOnCloud.Azure.RefreshToken
            ).first_item()
            if data is None or not data.client_id or not data.client_secret or not data.tenant_id or not data.access_token:
                return None, dict(
                    Code="AzureWasNotFound",
                    Message=f"Microsft Azure did not bestow '{app_name}'"
                )
            ret = AzureInfo()
            for k, v in data.items():
                setattr(ret, k, v)
            self.mem_cache_services.set_object(f"{self.cache_key}/{app_name}", ret)
            return ret, None

    # def get_upload_session(self, app_name: str, upload_id: str, client_file_name: str) -> str:
    #     access_info,error = self.get_azure_info(app_name)
    #     if error:
    #         return None,error
    #     # token = self.fucking_azure_account_service.acquire_token(
    #     #     app_name=app_name
    #     # )
    #     # drive_item_id = self.get_root_folder(
    #     #     app_name=app_name
    #     # )
    #     res_upload_session = call_ms_func(
    #         method="post",
    #         token=token,
    #         body={
    #             "item": {
    #                 "@microsoft.graph.conflictBehavior": "rename"
    #             },
    #             "deferCommit": False
    #         },
    #         api_url=f"/me/drive/items/root:/{drive_item_id}/{upload_id}/{client_file_name}:/createUploadSession",
    #         request_content_type="application/json",
    #         return_type=dict
    #     )
    #     return res_upload_session.get("uploadUrl")
    def get_all_folders(self, app_name, parent_id: str = "root", parent_path: str = None) -> typing.Tuple[
        AccquireTokenInfo | None, dict | None, dict | None]:

        token, error = self.acquire_token(app_name)

        if error:
            return None, None, error
        drive_id, error = self.get_driver_id(app_name)
        res, error = call_ms_func(
            method="get",
            api_url=f"drives/{drive_id}/items/{parent_id}/children",
            token=token.access_token,
            body=None
        )
        if error:
            return None, None, error
        else:
            items = res["value"]
            tree_hash = {}
            for x in items:
                fetch_key = f"{parent_path + '/' if parent_path is not None else ''}{x['name']}".lower()
                tree_item = {
                    fetch_key: dict(
                        name=x["name"],
                        id=x['id']
                    )
                }
                tree_hash = {**tree_hash, **tree_item}

                if x.get('folder', {}).get('childCount', 0) > 0:
                    sub_tree, sub_tree_hash, error = self.get_all_folders(app_name, x['id'], fetch_key)
                    if error:
                        return None, None, error
                    else:
                        x['children'] = sub_tree
                    tree_hash = {**tree_hash, **sub_tree_hash}

            return res["value"], tree_hash, None

    def get_driver_id(self, app_name) -> typing.Tuple[str | None, dict | None]:
        key = f"{self.cache_key}/{app_name}/driver_id"
        ret = self.mem_cache_services.get_str(key)
        if isinstance(ret, str):
            return ret, None
        token, error = self.acquire_token(app_name)
        if error:
            return None, error
        res, error = call_ms_func(
            method="get",
            api_url="me/drive",
            token=token.access_token,
            body=None
        )
        if error:
            return None, error
        else:
            self.mem_cache_services.set_str(key, res['id'])
            return res['id'], None
