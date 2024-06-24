import datetime
import gc
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_upload.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
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
from cyx.cloud.cloud_upload_google_service import CloudUploadGoogleService
from cy_jobs.cy_job_libs import JobLibs, screen_logs
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
screen_logs(__file__,"................")
from cyx.rabbit_utils import Consumer

consumer = Consumer(cyx.common.msg.MSG_CLOUD_GOOGLE_DRIVE_SYNC)
local_api_service = cy_kit.singleton(LocalAPIService)
cloud_upload_google_service = cy_kit.singleton(CloudUploadGoogleService)

if __name__ == "__main__":
    while True:
        try:
            msg = consumer.get_msg()
            if not msg:
                screen_logs(__file__,"no message")
                print(f"no message [{__file__}]")
                time.sleep(0.3)
                JobLibs.malloc_service.reduce_memory()
                continue
            method, properties, body = msg.method,msg.properties, msg.body
            data = {}
            if method:
                try:
                    data = json.loads(body)
                except:
                    time.sleep(0.3)
                    JobLibs.malloc_service.reduce_memory()
                    continue
                app_name = data["app_name"]
                upload_item = data["data"]
                full_path_on_cloud = upload_item.get("FullPathOnCloud")
                if full_path_on_cloud is None:
                    JobLibs.malloc_service.reduce_memory()
                    continue

                cloud_dir = pathlib.Path(full_path_on_cloud).parent.__str__()
                service, error = JobLibs.google_directory_service.g_drive_service.get_service_by_app_name(app_name)
                if error:
                    consumer.resume(msg)
                    JobLibs.malloc_service.reduce_memory()
                    continue
                download_url, rel_path, download_file, token, share_id = local_api_service.get_download_path(
                    upload_item,
                    app_name
                )
                if download_url is None:
                    del upload_item
                    JobLibs.malloc_service.reduce_memory()
                    continue
                screen_logs(__file__, f"sync file from {rel_path} to {full_path_on_cloud}")
                import googleapiclient.errors

                cloud_folder_id, error = JobLibs.google_directory_service.get_remote_folder_id(
                    service=service,
                    app_name=app_name,
                    directory=cloud_dir
                )

                if error:
                    screen_logs(__file__, f"sync file from {rel_path} to {full_path_on_cloud} is error {json.dumps(error,indent=4)}")
                    consumer.resume(msg)
                    JobLibs.malloc_service.reduce_memory()
                    continue
                full_path = os.path.join("/mnt/files", rel_path)
                if os.path.isfile(full_path):
                    try:
                        google_file_id, url_google_upload, error = JobLibs.google_directory_service.register_upload_file(
                                    app_name=app_name,
                                    directory_id = cloud_folder_id,
                                    file_name= upload_item["FileName"],
                                    file_size= upload_item["SizeInBytes"]
                                )
                        if error:
                            consumer.resume(msg)
                            del upload_item
                            JobLibs.malloc_service.reduce_memory()
                            continue
                        upload_item["google_file_id"] = google_file_id
                        screen_logs(__file__,f"{full_path} in {app_name} is synchronizing to Google Drive")
                        print(f"{full_path} in {app_name} is synchronizing to Google Drive")
                        if upload_item.get("google_file_id"):
                            try:
                                with open(full_path,"rb") as fs:
                                    with open(f"{full_path}.tmp","wb") as fw:
                                        data = fs.read(1024**2)
                                        while data:
                                            fw.write(data)
                                            del data
                                            JobLibs.malloc_service.reduce_memory()
                                            data = fs.read(1024 ** 2)
                                        del data
                                        JobLibs.malloc_service.reduce_memory()
                                ret, error = cloud_upload_google_service.do_upload(
                                    app_name=app_name,
                                    file_path=f"{full_path}.tmp",
                                    google_file_id=google_file_id,
                                    google_file_name=upload_item.get("FileName")

                                )
                                os.remove(f"{full_path}.tmp")
                                Repository.files.app(app_name).context.update(
                                    Repository.files.fields.Id == upload_item["_id"],
                                    Repository.files.fields.CloudId << google_file_id,
                                    Repository.files.fields.google_file_id << google_file_id
                                )
                                try:
                                    os.remove(full_path)
                                    Repository.cloud_file_sync.app(app_name).context.delete(
                                        Repository.cloud_file_sync.fields.UploadId == upload_item["_id"]
                                    )
                                except Exception as ex:
                                    Repository.cloud_file_sync.app(app_name).context.update(
                                        Repository.cloud_file_sync.fields.UploadId == upload_item["_id"],
                                        Repository.cloud_file_sync.fields.Status << 1,
                                        Repository.cloud_file_sync.fields.IsError << False
                                    )
                            except Exception as ex:
                                traceback_str = traceback.format_exc()
                                Repository.cloud_file_sync.app(app_name).context.update(
                                    Repository.cloud_file_sync.fields.UploadId == upload_item["_id"],
                                    Repository.cloud_file_sync.fields.IsError << True,
                                    Repository.cloud_file_sync.fields.ErrorOn << datetime.datetime.utcnow(),
                                    Repository.cloud_file_sync.fields.ErrorContent << traceback_str
                                )
                                print(traceback_str)
                                del upload_item
                                JobLibs.malloc_service.reduce_memory()
                                # msg_broker.delete(msg_info)
                    except Exception as ex:
                        traceback_str = traceback.format_exc()
                        Repository.cloud_file_sync.app(app_name).context.update(
                            Repository.cloud_file_sync.fields.UploadId == upload_item["_id"],
                            Repository.cloud_file_sync.fields.IsError << True,
                            Repository.cloud_file_sync.fields.ErrorOn << datetime.datetime.utcnow(),
                            Repository.cloud_file_sync.fields.ErrorContent << traceback_str
                        )
                        screen_logs(__file__, traceback_str)
                        print(traceback_str)
                        consumer.resume(msg)
                        del upload_item
                        JobLibs.malloc_service.reduce_memory()

            else:
                screen_logs(__file__, "No message received.")
                print("No message received.")
        except Exception as ex:
            str_err = traceback.format_exc()
            screen_logs(__file__, str_err)
            print(str_err)
        finally:
            JobLibs.malloc_service.reduce_memory()
