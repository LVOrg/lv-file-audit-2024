import datetime
import json
import typing

import fastapi.requests

import cy_kit
from cy_fucking_whore_microsoft.services.account_services import AccountService
from cy_fucking_whore_microsoft.fwcking_ms.caller import call_ms_func, FuckingWhoreMSApiCallException
from cy_fucking_whore_microsoft.services.services_models.onedive_drive_info import (
    DriverInfo,
    ShareInfo
)
from fastapi import UploadFile
from cyx.common.mongo_db_services import MongodbService
from cy_xdoc.models.apps import App
from cyx.cache_service.memcache_service import MemcacheServices


class OnedriveService:
    def __init__(self,
                 fucking_azure_account_service=cy_kit.singleton(AccountService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 memcache_service=cy_kit.singleton(MemcacheServices)
                 ):
        self.fucking_azure_account_service = fucking_azure_account_service
        self.mongodb_service = mongodb_service
        self.memcache_service = memcache_service

    def get_drive_info(self, app_name: str) -> DriverInfo:
        ret: DriverInfo = DriverInfo()
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        ret_data = call_ms_func(
            method="get",
            api_url='me/drive',
            token=token,
            body=None,
            return_type=dict,
            request_content_type=None
        )
        DriverInfo.ownerId = ""
        ret.driveType = ret_data.get("driveType", "")
        if (isinstance(ret_data.get("owner"), dict)
                and isinstance(ret_data.get("owner").get("user"), dict)):
            ret.ownerId = ret_data.get("owner").get("user").get("id")
            ret.ownerDisplayName = ret_data.get("owner").get("user").get("displayName")
        if isinstance(ret_data.get("quota"), dict):
            ret.total = ret_data.get("quota").get("total", 0)
            ret.remaining = ret_data.get("quota").get("remaining", 0)
        return ret

    def upload_file(self, app_name: str, file: UploadFile):
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
    def clear_cache(self, app_name):
        cache_key = f"{__file__}/{app_name}/get_root_folder"
        self.memcache_service.remove(cache_key)
    def get_root_folder(self, app_name) -> str:
        cache_key = f"{__file__}/{app_name}/get_root_folder"
        ret_root_folder = self.memcache_service.get_str(cache_key)
        if ret_root_folder is not None:
            return ret_root_folder
        fucking_one_drive_root_dir = self.fucking_azure_account_service.get_root_dir_of_one_drive(
            app_name=app_name
        )
        if fucking_one_drive_root_dir is not None:
            self.memcache_service.set_str(
                cache_key, fucking_one_drive_root_dir
            )
            return fucking_one_drive_root_dir
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )

        res = call_ms_func(
            method="get",
            api_url=f"me/drive/items/root/children?$filter=name eq '{fucking_one_drive_root_dir}'",
            token=token,
            body=None,
            return_type=dict,
            request_content_type=None
        )
        if len(res.get("value", [])) == 0:
            create_folder_data = {
                "name": fucking_one_drive_root_dir,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            res = call_ms_func(
                method="post",
                api_url=f"me/drive/items/root/children",
                token=token,
                body=create_folder_data,
                return_type=dict,
                request_content_type="application/json"
            )
            self.memcache_service.get_str(cache_key, fucking_one_drive_root_dir)
            return fucking_one_drive_root_dir
        return fucking_one_drive_root_dir

    def create_folder(self, app_name: str, folder_name: str):
        drive_item_id = self.get_root_folder(
            app_name=app_name
        )
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        ret = call_ms_func(
            method="post",
            token=token,
            api_url=f"/me/drive/items/root:/{drive_item_id}:/children",
            body={
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            },
            return_type=dict,
            request_content_type="application/json"
        )
        return ret

    def get_upload_session(self, app_name: str, upload_id: str, client_file_name: str) -> str:
        ret_create_folder = self.create_folder(
            app_name=app_name,
            folder_name=upload_id
        )
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        drive_item_id = self.get_root_folder(
            app_name=app_name
        )
        res_upload_session = call_ms_func(
            method="post",
            token=token,
            body={
                "item": {
                    "@microsoft.graph.conflictBehavior": "rename"
                },
                "deferCommit": False
            },
            api_url=f"/me/drive/items/root:/{drive_item_id}/{upload_id}/{client_file_name}:/createUploadSession",
            request_content_type="application/json",
            return_type=dict
        )
        return res_upload_session.get("uploadUrl")

    def upload_content(self, session_url: str, content: bytes, chunk_size: int, chunk_index: int, file_size: int):
        import requests
        request_chunk_size = chunk_size
        # if chunk_index == 0:
        #     if request_chunk_size > file_size:
        #         request_chunk_size = file_size
        _from = chunk_index*request_chunk_size
        _to =  min((chunk_index+1)*request_chunk_size,file_size)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(request_chunk_size),
            'Content-Range': f'bytes {_from}-{_to-1}/{file_size}'
        }

        # Send chunk
        res = requests.put(session_url, headers=headers, data=content, verify=False)
        res_data = json.loads(res.text)
        if res_data.get('error'):
            raise FuckingWhoreMSApiCallException(
                message=res_data.get('error').get("message"),
                code=res_data.get('error').get("code")

            )
        return res_data


    def get_access_item(self, app_name:str, upload_id:str, client_file_name:str):
        root_dir = self.get_root_folder(
            app_name=app_name
        )
        ret=f":/{root_dir}/{upload_id}/{client_file_name}:"
        return ret
    def get_share_info(self,
                        app_name:str,
                        upload_id:str,
                        scope:typing.Optional[str],
                        expiration: typing.Optional[datetime.datetime],
                        password: typing.Optional[str],
                        client_file_name: str)->ShareInfo:
        """
        https://graph.microsoft.com/v1.0/drive/root:/553ae3ba-037a-4fc4-bd8e-368b06692c06/b9ba361b-1379-4829-a9c9-c764e46faf3b/xx.mp4
        :param app_name:
        :param upload_id:
        :param client_file_name:
        :return:
        """

        #See link
        #https://techcommunity.microsoft.com/t5/sharepoint/making-onedrive-links-last-longer-or-be-renewable/m-p/321025
        scope = scope or "anonymous"
        ret: ShareInfo = ShareInfo()
        root_dir = self.get_root_folder(
            app_name=app_name
        )
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )

        ret.AccessItem = self.get_access_item(
            app_name=app_name,
            upload_id= upload_id,
            client_file_name = client_file_name
        )
        # exprire_time = datetime.datetime.utcnow() + datetime.timedelta(days=365 * 100)
        create_link_body = {
            "type": "view",
            "scope": scope
        }
        if isinstance(expiration,datetime.datetime):
            create_link_body["expirationDateTime"] = expiration.strftime("%Y-%m-%dT%H:%M:%SZ")
        if isinstance(password,str):
            create_link_body["password"] = password
        res_create_link = call_ms_func(
            method="post",
            api_url=f"drive/root{ret.AccessItem}/createLink",
            token=token,
            body=create_link_body,
            return_type=dict,
            request_content_type="application/json"

        )
        ret.ShareId = res_create_link["shareId"]
        #https://graph.microsoft.com/v1.0/shares/s!AhSDgZO1-y79gXMAavHFmnCU6Efy/driveItem
        res = call_ms_func(
            method="get",
            api_url=f"shares/{ret.ShareId}/driveItem",
            token=token,
            body=None,
            return_type=dict,
            request_content_type=None

        )
        ret.ContentUrl =res.get("@microsoft.graph.downloadUrl")
        ret.Id = res.get('id')
        ret.WebUrl = res.get('webUrl')

        return ret
        from cy_fucking_whore_microsoft.fwcking_ms.caller import URL as grap_url
        # return f"/shares/{share_id}:/{root_dir}/{upload_id}/{client_file_name}:/content"
        # return f"{grap_url}/drive/root:/{root_dir}/{upload_id}/{client_file_name}:/content"

    def delete_upload(self, app_name:str, upload_id:str):
        root_dir = self.get_root_folder(
            app_name=app_name
        )
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        res = call_ms_func(
            method="delete",
            api_url=f"drive/root:/{root_dir}/{upload_id}",
            token=token,
            body=None,
            return_type=dict,
            request_content_type=None

        )
        return res

    def get_content(self, app_name:str, upload_id:str,client_file_name:str, request:fastapi.requests.Request):
        from fastapi.responses import StreamingResponse
        import mimetypes
        cache_key = f"{__file__}/{type(self).__name__}/get_content/{app_name}/{upload_id}"

        content_type,_ = mimetypes.guess_type(client_file_name)
        # URL of the video content on the other website
        content_url = self.memcache_service.get_str(cache_key)
        if content_url is None:
            content_url  = self.get_url_content(
                app_name,
                upload_id,
                client_file_name
            )

        from requests import get
        # Send a GET request to the video URL
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        HEADERS = {
            'Authorization': 'Bearer ' + token,

        }
        if request.headers.get('range'):
            HEADERS = {
                'range': request.headers.get('range'),
                'Authorization': 'Bearer ' + token

            }
        expire_time = request.headers.get('Expires')
        response = get(content_url, stream=True,headers=HEADERS)
        if response.headers.get('Content-Location'):
            self.memcache_service.set_str(cache_key,response.headers.get('Content-Location'),11*30*24*60)
        # Set response headers for streaming
        response.headers["Content-Type"] = content_type
        response.headers["Accept-Ranges"] = "bytes"
        # response.headers["Content-Range"] = request.headers.get('range')
        if response.headers.get("Content-Disposition"):
            del response.headers['Content-Disposition']
        # Return StreamingResponse object
        return StreamingResponse(
            content=response.iter_content(chunk_size=1024*4),
            headers=response.headers,
            media_type=content_type,
            status_code= response.status_code
        )

    def get_url_content(self, app_name, upload_id,client_file_name):
        from cy_fucking_whore_microsoft.fwcking_ms.caller import URL
        access_item = self.get_access_item(
            app_name=app_name,
            upload_id=upload_id,
            client_file_name=client_file_name
        )
        ret= f"{URL}me/drive/root{access_item}/content"
        return ret






