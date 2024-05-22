import datetime
import json
import os
import typing

import requests

import cy_docs
import cy_kit
from cyx.repository import Repository
from msgraph import GraphServiceClient
from azure.identity.aio import ClientSecretCredential
from cyx.cloud.azure.azure_utils import call_ms_func
from cyx.cloud_cache_services import CloudCacheService
from fastapi.responses import JSONResponse


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
    def __init__(self,
                 mem_cache_services: MemcacheServices = cy_kit.singleton(MemcacheServices),
                 cloud_cache_service: CloudCacheService = cy_kit.singleton(CloudCacheService)):
        self.cache_key = f"{type(self).__module__}/{type(self).__name__}/v1"
        self.mem_cache_services = mem_cache_services
        self.cloud_cache_service = cloud_cache_service

    def get_credential(self, app_name: str) -> typing.Tuple[ClientSecretCredential | None, dict | None]:
        azure_info, error = self.get_azure_info(app_name)
        if error:
            return None, error

        credential = ClientSecretCredential(azure_info.tenant_id,
                                            azure_info.client_id,
                                            azure_info.client_secret)
        return credential, None

    def __get_token_info__(self, app_name):
        azure_info, error = self.get_azure_info(app_name)
        post_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        if (not hasattr(azure_info, "refresh_token") or
                not hasattr(azure_info, "client_id") or
                not hasattr(azure_info, "scope")
                or not hasattr(azure_info, "client_secret")):
            return None, dict(Code="InvalidSettings", Message=f"Azure settings for {app_name} is invalid")
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
            return ret, None

    def acquire_token(self, app_name, reset=False) -> typing.Tuple[AccquireTokenInfo | None, dict | None]:
        """
        This method get access token of a certain app. For Azure before call any GraphAPI. please. call this method \n
        first for access token. Yeah! this method priority get from cache first if the return token from cache was on \n
        time return that value instead acquire new access token If thou want to reset cache Get token info of app \n
        where link to Azure :param app_name: :param reset: :return: acquire_token_info, error
        ------------------\n
        Phương pháp này nhận mã thông báo truy cập của một ứng dụng nhất định. Đối với Azure trước khi gọi bất kỳ GraphAPI nào. Xin vui lòng. gọi phương thức này \n
        đầu tiên cho mã thông báo truy cập. Vâng! Phương thức này ưu tiên nhận từ bộ đệm trước nếu bộ đệm biểu mẫu mã thông báo trả về được bật \n
        thời gian trả lại giá trị đó thay vì nhận mã thông báo truy cập mới Nếu bạn muốn đặt lại bộ đệm Nhận thông tin mã thông báo của ứng dụng \n
        nơi liên kết đến Azure :param app_name: :param reset: :return: Acacqui_token_info, lỗi
        """
        key = f"{self.cache_key}/{app_name}/token"
        if not reset:

            ret = self.mem_cache_services.get_object(key, AccquireTokenInfo)
            if ret is not None and (ret.expires_on - datetime.datetime.utcnow()).total_seconds() > 5:
                return ret, None
            token_info, error = self.__get_token_info__(app_name)
            if error:
                return None, error
            self.mem_cache_services.set_object(key, token_info)
            return token_info, None
        else:
            token_info, error = self.__get_token_info__(app_name)
            if error:
                return None, error
            self.mem_cache_services.set_object(key, token_info)
            return token_info, None

    def get_azure_info(self, app_name) -> typing.Tuple[AzureInfo | None, dict | None]:
        """
        Get all info has been set up for app
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

    async def get_content_async(self, app_name, upload_id: str, cloud_file_id, content_type: str, request, nocache=False,download_only=False):
        import cy_web
        from fastapi.responses import StreamingResponse
        if not nocache:
            cache_file_path = self.cloud_cache_service.get_from_cache(upload_id)
            if cache_file_path:
                fs = open(cache_file_path, "rb")

                def get_size():
                    return os.stat(cache_file_path).st_size

                setattr(fs, "get_size", get_size)
                ret = await cy_web.cy_web_x.streaming_async(
                    fs, request, content_type, streaming_buffering=1024 * 4 * 3 * 8
                )
                return ret
        cache_key = f"{__file__}/{type(self).__name__}/get_content/{app_name}/{cloud_file_id}"
        content_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{cloud_file_id}/content"
        from requests import get
        token_info, error = self.acquire_token(app_name)
        if error:
            return JSONResponse(content=error, status_code=404)
        token = token_info.access_token
        HEADERS = {
            'Authorization': 'Bearer ' + token,

        }
        if request.headers.get('range'):
            HEADERS = {
                'range': request.headers.get('range'),
                'Authorization': 'Bearer ' + token

            }
        expire_time = request.headers.get('Expires')
        import requests
        response = requests.get(content_url, stream=True, headers=HEADERS, verify=False)
        if response.status_code == 401:
            token_info, error = self.acquire_token(app_name, reset=True)
            if error:
                return JSONResponse(content=error, status_code=500)
            token = token_info.access_token
            HEADERS["Authorization"] = f'Bearer {token}'
            response = requests.get(content_url, stream=True, headers=HEADERS)
        if response.status_code >= 300:
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=response.text, status_code=response.status_code)

        if response.headers.get('Content-Location'):
            self.mem_cache_services.set_str(cache_key, response.headers.get('Content-Location'), 60)
        if response.status_code == 404:
            self.mem_cache_services.remove(cache_key)

            response = get(content_url, stream=True, headers=HEADERS)

            if response.headers.get('Content-Location'):
                self.mem_cache_services.set_str(cache_key, response.headers.get('Content-Location'), 60)
        # Set response headers for streaming
        response.headers["Content-Type"] = content_type
        response.headers["Accept-Ranges"] = "bytes"
        # response.headers["Content-Range"] = request.headers.get('range')
        if response.headers.get("Content-Disposition") and not download_only:
            del response.headers['Content-Disposition']
        if content_type.startswith("image/"):
            self.cloud_cache_service.cache_content(app_name=app_name, upload_id=upload_id, url=content_url,
                                                   cloud_id=cloud_file_id, header=HEADERS)
        # Return StreamingResponse object
        return StreamingResponse(
            content=response.iter_content(chunk_size=1024 * 4),
            headers=response.headers,
            media_type=content_type,
            status_code=response.status_code
        )

    # def get_url_content(self, app_name, upload_id, client_file_name):
    #     URL = 'https://graph.microsoft.com/v1.0/'
    #
    #
    #     access_item = f":/roor/{upload_id}/{client_file_name}:"
    #     # access_item = self.get_access_item(
    #     #     app_name=app_name,
    #     #     upload_id=upload_id,
    #     #     client_file_name=client_file_name
    #     # )
    #     ret = f"{URL}me/drive/root{access_item}/content"
    #     return ret

    def get_access_item(self, app_name, upload_id, client_file_name):
        pass
