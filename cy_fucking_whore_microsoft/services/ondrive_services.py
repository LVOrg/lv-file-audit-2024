import cy_kit
from cy_fucking_whore_microsoft.services.account_services import AccountService
from cy_fucking_whore_microsoft.fwcking_ms.caller import call_ms_func
from cy_fucking_whore_microsoft.services.services_models.onedive_drive_info import DriverInfo
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
                cache_key,fucking_one_drive_root_dir
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
            self.memcache_service.get_str(cache_key,fucking_one_drive_root_dir)
            return fucking_one_drive_root_dir
        return fucking_one_drive_root_dir

    def create_folder(self, app_name:str,folder_name:str):
        drive_item_id = self.get_root_folder(
            app_name=app_name
        )
        token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        ret = call_ms_func(
            method="post",
            token=token,
            api_url=f"/me/drive/items/root:/drive_item_id/{folder_name}:/children",
            body={
              "name": "New Folder",
              "folder": { },
              "@microsoft.graph.conflictBehavior": "rename"
            },
            return_type=dict,
            request_content_type="application/json"
        )
        return ret
    def get_upload_session(self, app_name:str,upload_id:str, client_file_name:str)->str:
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
                "deferCommit": True
            },
            api_url=f"/me/drive/items/root:/{drive_item_id}/upload_id/{client_file_name}:/createUploadSession",
            request_content_type="application/json",
            return_type=dict
        )
        return res_upload_session.get("uploadUrl")
