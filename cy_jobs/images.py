"""
This consumer will receive message 'files.upload' from broker. Then generate some messages and pervasive them to
other consumer
---------------------------------------------------------
Consumer này sẽ nhận được tin nhắn 'files.upload' từ broker. Sau đó, tạo một số thông điệp và phổ biến chúng đến Consumer khác
--------------------------------------------

MSG_FILE_UPLOAD
├── MSG_FILE_GENERATE_IMAGE_FROM_VIDEO (*here*)
│   ├── MSG_FILE_GENERATE_PDF_FROM_IMAGE
│   │   └── MSG_FILE_OCR_CONTENT
│   │       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
│   └── MSG_FILE_GENERATE_THUMBS
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB
│       └── MSG_FILE_SAVE_CUSTOM_THUMB
├── MSG_FILE_EXTRACT_TEXT_FROM_VIDEO
├── MSG_FILE_GENERATE_IMAGE_FROM_OFFICE
│   └── MSG_FILE_GENERATE_THUMBS
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB
│       └── MSG_FILE_SAVE_CUSTOM_THUMB
├── MSG_FILE_GENERATE_IMAGE_FROM_PDF
│   └── MSG_FILE_OCR_CONTENT
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
├── MSG_FILE_GENERATE_PDF_FROM_IMAGE
│   └── MSG_FILE_OCR_CONTENT
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
├── MSG_FILE_GENERATE_THUMBS
│   ├── MSG_FILE_SAVE_DEFAULT_THUMB
│   └── MSG_FILE_SAVE_CUSTOM_THUMB
└── MSG_FILE_OCR_CONTENT
    └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE

"""
import datetime
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_upload.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
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
from cyx.content_services import ContentService,ContentTypeEnum
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
import  cy_utils
import cy_utils.texts
import mimetypes
from cy_xdoc.services.search_engine import SearchEngine
import gradio_client
print(gradio_client.__version__)
from gradio_client import Client
from cyx.processing_file_manager_services import ProcessManagerService
def get_doc_type(file_ext: str) -> str:
    file_ext = file_ext.lower()
    mime_type, _ = mimetypes.guess_type(f"a.{file_ext}")
    if mime_type.startswith("image/"):
        return "image"
    elif file_ext.lower() == "pdf":
        return "pdf"
    elif mime_type.startswith("video/"):
        return "video"
    elif file_ext in config.ext_office_file:
        return "office"
    else:
        return "unknown"
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_IMAGE)
class Process:
    def __init__(self,
                 shared_storage_service=cy_kit.singleton(ShareStorageService),
                 content_service= cy_kit.singleton(ContentService),
                 # logger=cy_kit.singleton(LoggerService),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 search_engine=cy_kit.singleton(SearchEngine),
                 process_manager_service=cy_kit.singleton(ProcessManagerService)
                 ):
        # self.logger = logger
        self.content_service = content_service

        self.temp_file = temp_file

        self.output_dir = shared_storage_service.get_temp_dir(self.__class__)
        self.local_api_service = local_api_service
        self.search_engine = search_engine
        self.process_services_host = config.process_services_host or "http://localhost"
        self.process_manager_service = process_manager_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        print(f'{msg_info.Data.get("MainFileId")}')
        try:
            download_url, rel_path, download_file, token, share_id = self.local_api_service.get_download_path(msg_info.Data, msg_info.AppName)
            if download_url is None:
                msg.delete(msg_info)
                return
            server_image_file_path = f"{rel_path}.png"
            file_item = Repository.files.app(msg_info.AppName).context.find_one(
                Repository.files.fields.id == msg_info.Data["_id"]
            )
            if not file_item:
                msg.delete(msg_info)
                return
            is_ready_image = (file_item.ProcessInfo or {}).get('image') and (
                        (file_item.ProcessInfo or {}).get('image', {}).get("IsError", "False") == "False")
            if is_ready_image:
                msg.delete(msg_info)
                return
            process_services_host = config.process_services_host or "http://localhost"
            file_ext = pathlib.Path(file_item[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
            doc_type = get_doc_type(file_ext)
            action_info = getattr(config.process_services, doc_type)
            client = Client(f"{process_services_host}:{action_info.get('image').get('port')}/")
            _, result = client.predict(
                download_url,
                False,
                api_name="/predict"
            )
            image_file_path = f"{rel_path}.png"
            if os.path.isfile(result):
                self.local_api_service.send_file(
                    file_path=result,
                    token=token,
                    local_share_id=share_id,
                    app_name=msg_info.AppName,
                    rel_server_path=image_file_path

                )
                if os.path.isfile(result):
                    os.remove(result)
            msg.delete(msg_info)
        except Exception as ex:
            raise ex
            self.process_manager_service.submit_error(
                data=file_item,
                app_name=msg_info.AppName,
                action_type="image",
                error=ex

            )
            msg.delete(msg_info)


