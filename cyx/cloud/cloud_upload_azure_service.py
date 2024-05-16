import json
import time
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
from cyx.cloud.azure.azure_utils import call_ms_func
class CloudUploadAzureService:
    def __init__(self, azure_utils_service:AzureUtilsServices= cy_kit.singleton(AzureUtilsServices)):
        self.azure_utils_service = azure_utils_service
    def do_upload(self, app_name:str, file_path:str, azure_file_name:str,azure_file_id:str=None)->typing.Tuple[str|None,dict|None]:
        token,error = self.azure_utils_service.acquire_token(
            app_name=app_name
        )
        if error:
            return None, error
        access_token = token.access_token
        server_path = file_path.replace(f"/mnt/files/{app_name}/","")
        print(f"Checking folder path {pathlib.Path(server_path).parent.__str__()}")
        folder_id, error = self.check_server_path_by_access_token(
            path=pathlib.Path(server_path).parent.__str__(),
            access_token=token.access_token
        )
        if error:
            print(f"Checking folder path {pathlib.Path(server_path).parent.__str__()} is error")
            print(json.dumps(error,indent=4))
            return None, error
        print(f"Checking folder path {pathlib.Path(server_path).parent.__str__()} is ok")
        print(f"Preparing upload file {server_path} ...")
        res_upload_session, error = call_ms_func(
            method="post",
            token=access_token,
            body={
                "item": {
                    "@microsoft.graph.conflictBehavior": "rename"
                },
                "deferCommit": False
            },
            api_url=f"/me/drive/items/root:/{pathlib.Path(server_path).parent.__str__()}/{azure_file_name}:/createUploadSession",
            request_content_type="application/json"
        )
        if error:
            print(f"Preparing upload file {server_path} is error")
            print(json.dumps(error, indent=4))
            return  None,error
        uploadUrl=res_upload_session.get("uploadUrl")
        print(f"Preparing upload file {server_path} is ok")
        print(f"Content will be uploaded at {uploadUrl}")
        res_data = {}
        is_uploaded = False
        upload_size=0
        file_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file:

            chunk_size = 1024 * 32  # 1 MB chunks\

            # progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
            for start_byte in range(0, file_size, chunk_size):
                end_byte = min(start_byte + chunk_size, file_size) - 1
                #f'bytes {_from}-{_to-1}/{file_size}'
                content_range = f"bytes {start_byte}-{end_byte}/{file_size}"
                headers = {
                    'Content-Type': 'application/octet-stream',
                    'Content-Length': str(chunk_size),
                    'Content-Range': content_range
                }
                chunk = file.read(chunk_size)
                upload_size+=len(chunk)
                response = requests.put(uploadUrl, headers=headers, data=chunk,stream=False)


                count=10
                try:
                    res_data = response.json()
                    count=0
                    print("\033c", end="")
                    print(f"{server_path} uploaded  {content_range}")
                except Exception as ex:
                    is_fail= True
                    while count>0:
                        print("\033c", end="", flush=True)
                        print(f"Content uploaded  fail retry on the next 0.3")
                        time.sleep(0.3)
                        try:
                            response = requests.put(uploadUrl, headers=headers, data=chunk)
                            res_data = response.json()
                            count = 0
                            is_fail= False
                            print("\033c", end="", flush=True)
                            print(f"{server_path} uploaded  {content_range}")
                        except:
                            count-=1
                    if is_fail:
                        print(f"Content upload to {uploadUrl} was fail after 10 time re-try")
                        return None, dict(
                            Code="UploadFailAfter10TimeRetry",
                            Message = f"Content upload to {uploadUrl} was fail after 10 time re-try"

                        )

                # progress_bar.update(len(chunk))
                if res_data.get("error"):
                    return  None, dict(
                        Code=res_data.get("error").get("code"),
                        Message=res_data.get("error").get("message")
                    )
        print(f"Content upload to {uploadUrl} was finishs")
        return res_data['id'], None
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



