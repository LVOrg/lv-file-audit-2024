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
@broker(message=cyx.common.msg.MSG_FILE_UPLOAD)
class Process:
    def __init__(self,
                 shared_storage_service=cy_kit.singleton(ShareStorageService),
                 content_service= cy_kit.singleton(ContentService),
                 # logger=cy_kit.singleton(LoggerService),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 search_engine=cy_kit.singleton(SearchEngine)
                 ):
        # self.logger = logger
        self.content_service = content_service
        print(f"consumer {cyx.common.msg.MSG_FILE_UPLOAD} init")
        self.temp_file = temp_file

        self.output_dir = shared_storage_service.get_temp_dir(self.__class__)
        self.local_api_service = local_api_service
        self.search_engine = search_engine
        self.process_services_host = config.process_services_host or "http://localhost"

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        print(f'{msg_info.Data.get("MainFileId")}')
        try:
            download_url, rel_path, download_file, token, share_id = self.local_api_service.get_download_path(msg_info.Data, msg_info.AppName)
            if download_url is None:
                msg.delete(msg_info)
                return
            file_context = Repository.files.app(msg_info.AppName).context
            file_item = Repository.files.app(msg_info.AppName).context.find_one(
                Repository.files.fields.id== msg_info.Data["_id"]
            )
            if not file_item:
                msg.delete(msg_info)
                return
            is_ready_content = (file_item.ProcessInfo or {}).get('content') and ( (file_item.ProcessInfo or {}).get('content',{}).get("IsError","False")=="False")

            is_ready_image = (file_item.ProcessInfo or {}).get('image') and ( (file_item.ProcessInfo or {}).get('image',{}).get("IsError","False")=="False")
            file_ext = file_item[Repository.files.fields.FileExt]
            if file_ext is None:
                file_ext = pathlib.Path(file_item[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
            doc_type = get_doc_type(file_ext)
            if doc_type=="unknown":
                msg.delete(msg_info)
                return
            # if is_ready_content and is_ready_image:
            #     msg.delete(msg_info)
            #     return
            action_info = getattr(config.process_services, doc_type)
            if not is_ready_content:
                try:
                    content = None
                    action = action_info['content']
                    if action['type']=='tika':
                        content = cy_utils.call_local_tika(
                            action=action,
                            action_type="content",
                            url_file= download_url,
                            download_file=""
                        )
                    elif action['type'] == 'web-api':
                        content = cy_utils.call_web_api(data=action,action_type="content",url_file=download_url,download_file=download_file)

                    if content:

                        content = cy_utils.texts.well_form_text(content)
                        self.search_engine.update_content(
                            app_name= msg_info.AppName,
                            id = msg_info.Data["_id"],
                            content=content,
                            replace_content=True,
                            data_item= file_item
                        )
                        print(f"update content for {rel_path}")

                    if file_item.ProcessInfo is None:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            Repository.files.fields.ProcessInfo << {"content": dict(

                                IsError=False,
                                Error="",
                                UpdateTime=datetime.datetime.utcnow(),

                            )}
                        )
                    else:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            getattr(Repository.files.fields.ProcessInfo, "content") << dict(
                                IsError=False,
                                Error="",
                                UpdateTime=datetime.datetime.utcnow(),

                            )
                        )

                except Exception as ex:
                    print(str(ex))
                    if file_item[Repository.files.fields.ProcessInfo] is None:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            Repository.files.fields.ProcessInfo << {"content": dict(

                                IsError=True,
                                Error=str(ex),
                                UpdateTime=datetime.datetime.utcnow(),

                            )}
                        )
                    else:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            getattr(Repository.files.fields.ProcessInfo, "content") << dict(
                                IsError=True,
                                Error=str(ex),
                                UpdateTime=datetime.datetime.utcnow(),

                            )
                        )
                    return
            if not is_ready_image:
                try:
                    action = action_info['image']
                    client = Client(f"{self.process_services_host}:{action.get('port')}/")
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
                        print(f"update image for {rel_path}")
                    if file_item.ProcessInfo is None:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            Repository.files.fields.ProcessInfo << {"image": dict(

                                IsError=False,
                                Error="",
                                UpdateTime=datetime.datetime.utcnow(),

                            )}
                        )
                    else:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            getattr(Repository.files.fields.ProcessInfo, "image") << dict(
                                IsError=False,
                                Error="",
                                UpdateTime=datetime.datetime.utcnow(),

                            )
                        )
                except Exception as ex:
                    print(str(ex))
                    if file_item[Repository.files.fields.ProcessInfo] is None:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            Repository.files.fields.ProcessInfo << {"image": dict(

                                IsError=True,
                                Error=str(ex),
                                UpdateTime=datetime.datetime.utcnow(),

                            )}
                        )
                    else:
                        file_context.update(
                            Repository.files.fields.id == file_item.id,
                            getattr(Repository.files.fields.ProcessInfo, "image") << dict(
                                IsError=True,
                                Error=str(ex),
                                UpdateTime=datetime.datetime.utcnow(),

                            )
                        )
                    return
                finally:
                    if os.path.isfile(download_file):
                        os.remove(download_file)
            msg.delete(msg_info)
        except Exception as ex:
            raise ex


