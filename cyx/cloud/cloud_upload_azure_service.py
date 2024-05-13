import typing

import cy_kit
from cyx.g_drive_services import GDriveService
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm
import os
import cy_file_cryptor.context
from cyx.common import config
cy_file_cryptor.context.set_server_cache(config.cache_server)
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
import cy_file_cryptor.wrappers
class CloudUploadAzureService:
    def __init__(self, azure_utils_service:AzureUtilsServices= cy_kit.singleton(AzureUtilsServices)):
        self.azure_utils_service = azure_utils_service
    def do_upload(self, app_name:str, file_path:str, azure_file_name:str,azure_file_id:str=None):
        token = self.azure_utils_service.acquire_token(
            app_name=app_name
        )