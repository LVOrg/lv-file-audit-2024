import typing
import requests
import cy_kit
from cyx.g_drive_services import GDriveService
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm
import os
import cy_file_cryptor.context
from cyx.common import config
cy_file_cryptor.context.set_server_cache(config.cache_server)
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
import pathlib
import cy_file_cryptor.wrappers
from urllib import parse
class CloudUploadAzureService:
    def __init__(self, azure_utils_service:AzureUtilsServices= cy_kit.singleton(AzureUtilsServices)):
        self.azure_utils_service = azure_utils_service
    def do_upload(self, app_name:str, file_path:str, azure_file_name:str,azure_file_id:str=None):
        token,error = self.azure_utils_service.acquire_token(
            app_name=app_name
        )
        if error:
            return None, error
        access_token = token.access_token
        server_path = file_path.replace(f"/mnt/files/{app_name}/","")
        folder_id, error = self.check_server_path_by_access_token(
            path=pathlib.Path(server_path).parent.__str__(),
            access_token=token.access_token
        )
        uri_path = parse.quote_plus(f"{pathlib.Path(server_path).parent.__str__()}/{azure_file_name}")
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}:/{azure_file_name}:/createUploadSession"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        # payload = {
        #     'item': {
        #         '@microsoft.graph.conflictBehavior': 'rename',  # Define what happens if there's a naming conflict
        #         'name': file_name
        #     }
        # }
        item={
          "description": "test",
          "fileSize": os.stat(file_path).st_size,
          "fileSystemInfo": {"@odata.type": "microsoft.graph.fileSystemInfo"},
          "name": azure_file_name
        }
        data = {"item": item}  # Replace with your filename

        response = requests.post(url, headers=headers, json=data)

    def get_folder_id(self,access_token, folder_path)->typing.Tuple[str|None,dict|None]:
        """Checks for folder existence and creates it if not in conflict.

        Args:
            access_token: Your Microsoft access token.
            parent_id: The ID of the parent folder where the new folder will be created.
                       Use "root" for the root folder.
            folder_name: The name of the new folder to create.

        Returns:
            The ID of the newly created folder on success (if no conflict), None otherwise.
        """

        #https://graph.microsoft.com/v1.0/me/drive/root:/2024/05
        url=f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}"

        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("error"):
            if data.get("error").get("code")=="itemNotFound" and response.status_code==404:
                return None,None
            return None, dict(
                Code = data.get("error").get("code"),
                Message = data.get("error").get("message")
            )
        else:
            return data.get("id"),None


    def check_server_path_by_access_token(self, access_token, path)->typing.Tuple[str|None, dict|None]:
        dirs = path.split('/')
        folder_id, error = self.get_folder_id(access_token, "/".join(dirs))
        if error:
            return None, error
        elif folder_id is not None:
            return folder_id, None
        else:
            folder_id,error = self.check_server_path_by_access_token(access_token,"/".join(dirs[0:-1]))
            if error:
                return None,error
            else:
                url = f"https://graph.microsoft.com/v1.0//me/drive/items/{folder_id}/children"
                headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
                folder_name = pathlib.Path(path).name
                data = {
                    "name": folder_name,
                    "folder": { }
                }  # Folder data
                response = requests.post(url, headers=headers, json=data)
                data = response.json()
                if data.get("error"):
                    return  None,dict(
                        Code= data.get("error").get("code"),
                        Message = data.get("error").get("message")
                    )
                else:
                    return data["id"],None
                parent_id = response.json()["id"]
        # while len(check_path)>0:
        #     folder_id, error = self.get_folder_id(access_token, "/".join(check_path))
        #     if error:
        #         return None,error
        #     elif folder_id is not None:
        #         return folder_id, None
        #     else:
        #         if parent_id is None:
        #             url = f"https://graph.microsoft.com/v1.0/me/drive/root/children"
        #         else:
        #             url = f"https://graph.microsoft.com/v1.0//me/drive/items/{parent_id}/children"
        #         headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        #         data = {
        #             "name": dir,
        #             "folder": { }
        #         }  # Folder data
        #
        #         response = requests.post(url, headers=headers, json=data)
        #         data = response.json()
        #         if data.get("error"):
        #             return  None,dict(
        #                 Code= data.get("error").get("code"),
        #                 Message = data.get("error").get("message")
        #             )
        #         parent_id = response.json()["id"]
        # for dir in dirs:
        #     check_path+=[dir]
        #     folder_id, error =self.get_folder_id(access_token,"/".join(check_path))
        #     if error:
        #         return None,error
        #     elif folder_id is None:
        #         if parent_id is None:
        #             url = f"https://graph.microsoft.com/v1.0/me/drive/root/children"
        #         else:
        #             url = f"https://graph.microsoft.com/v1.0//me/drive/items/{parent_id}/children"
        #         headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        #         data = {
        #             "name": dir,
        #             "folder": { }
        #         }  # Folder data
        #
        #         response = requests.post(url, headers=headers, json=data)
        #         data = response.json()
        #         if data.get("error"):
        #             return  None,dict(
        #                 Code= data.get("error").get("code"),
        #                 Message = data.get("error").get("message")
        #             )
        #         parent_id = response.json()["id"]
        #     else:
        #             parent_id = folder_id
        # return parent_id, None

