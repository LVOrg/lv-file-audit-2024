import datetime
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_upload.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)
# from cyx.loggers import LoggerService
from cyx.content_services import ContentService, ContentTypeEnum
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
import cy_utils
import cy_utils.texts
import mimetypes
from cy_xdoc.services.search_engine import SearchEngine
# import gradio_client
# print(gradio_client.__version__)
from gradio_client import Client
from cyx.processing_file_manager_services import ProcessManagerService
from cyx.cloud.cloud_upload_azure_service import CloudUploadAzureService
import traceback
import pika
import json



def is_file_deletable(filepath):
    """
    Checks if a file can be deleted based on permissions and status.

    Args:
        filepath (str): The path to the file.

    Returns:
        bool: True if the file is likely deletable, False otherwise.
    """

    if not os.path.exists(filepath):
        return False  # File doesn't exist

    try:
        # Check file permissions
        stat = os.stat(filepath)
        if not os.access(filepath, os.W_OK):  # Check for write permission on the file
            return False
        if not os.access(os.path.dirname(filepath), os.W_OK | os.X_OK):  # Check write and execute on directory
            return False

        # Check if file is open (may not be foolproof)
        with open(filepath, 'x'):  # Try to open in exclusive mode (fails if open)
            pass
        return True
    except (OSError, PermissionError):
        return False  # Handle permission or other errors


"""
host=self.__server__,
                    port=self.__port__,
                    virtual_host='/',
                    credentials=self.__credentials__,
                    heartbeat=30,
                    retry_delay=10
"""
from cyx.rabbit_utils import Consumer
consumer = Consumer(cyx.common.msg.MSG_CLOUD_ONE_DRIVE_SYNC)
local_api_service = cy_kit.singleton(LocalAPIService)
cloud_upload_azure_service = cy_kit.singleton(CloudUploadAzureService)

while True:
    try:
        msg = consumer.get_msg()
        if not msg:
            continue
        download_url, rel_path, download_file, token, share_id = local_api_service.get_download_path(msg.data,
                                                                                                     msg.app_name)
        full_path = os.path.join("/mnt/files",rel_path)
        if os.path.isfile(full_path):
            try:
                print(f"Upload {full_path} to onedrive")
                file_id, error = cloud_upload_azure_service.do_upload(
                    app_name=msg.app_name,
                    file_path=full_path,
                    azure_file_id=None,
                    azure_file_name=msg.data.get("FileName")
                )
                if error:
                    txt_error = json.dumps(error,indent=4)
                    print(txt_error)
                    Repository.cloud_file_sync.app(msg.app_name).context.update(
                        Repository.cloud_file_sync.fields.UploadId == msg.data["_id"],
                        # Repository.cloud_file_sync.fields.Status << 1,
                        Repository.cloud_file_sync.fields.IsError << True,
                        Repository.cloud_file_sync.fields.ErrorContent<< txt_error,
                        Repository.cloud_file_sync.fields.ErrorOn << datetime.datetime.utcnow()
                    )
                    continue

                Repository.files.app(msg.app_name).context.update(
                                            Repository.files.fields.Id == msg.data["_id"],
                                            Repository.files.fields.CloudId << file_id
                                        )
                Repository.cloud_file_sync.app(msg.app_name).context.delete(
                    Repository.cloud_file_sync.fields.UploadId == msg.data["_id"]
                )
                Repository.cloud_file_sync.app(msg.app_name).context.update(
                    Repository.cloud_file_sync.fields.UploadId == msg.data["_id"],
                    Repository.cloud_file_sync.fields.Status << 1,
                    Repository.cloud_file_sync.fields.IsError << False
                )
                try:
                    os.remove(full_path)
                except Exception as ex:
                    print(f"{full_path} is in processing")

            except:
                print(traceback.format_exc())
                consumer.resume(msg)


    except Exception as ex:
        str_err=traceback.format_exc()
        print(str_err)
