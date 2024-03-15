# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_video.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
import uuid
from datetime import time
import os
import cv2
import numpy

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
from cy_file_cryptor import wrappers
import cyx.framewwork_configs
import os.path
import pathlib

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
from cyx.media.pdf import PDFService
from cyx.media.video import VideoServices

import json

temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)

msg = cy_kit.singleton(RabitmqMsg)
from cyx.loggers import LoggerService
from cyx.common.msg import broker
from cyx.content_services import ContentService, ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.local_api_services import LocalAPIService


@broker(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 temp_file=cy_kit.singleton(TempFiles),
                 video_service=cy_kit.singleton(VideoServices),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 local_api_service=cy_kit.singleton(LocalAPIService)
                 ):
        self.logger = logger
        self.temp_file = temp_file
        self.video_service = video_service
        self.content_service = content_service
        self.mongodb_service = mongodb_service
        self.local_api_service = local_api_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):

        # api/hps-file-test/file/e5524d97-467e-4c96-99d0-21c5c36a4349/piano.mp4
        # http://172.16.7.99/lvfile/api/lv-docs/file/1c387233-9bf8-4a0d-939d-bbcec7bf36c6/bandicam%202023-08-11%2011-51-55-581.mp4
        main_file_id = msg_info.Data["StoragePath"]
        # /lvfile/api/sys/admin/content-share/{rel_path}
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + main_file_id.split("://")[1]
        # resource = self.content_service.get_resource(msg_info)
        # docs = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
        # if resource is None:
        #     msg.delete(msg_info)
        #     return
        # if not os.path.isfile(resource):
        #     docs.context.update(
        #         docs.fields.id==msg_info.Data["_id"],
        #         docs.fields.ThumbnailsAble<<False
        #     )
        #     msg.delete(msg_info)
        #     return
        local_share_id = None
        token = None
        if hasattr(msg_info.Data, "local_share_id"):
            local_share_id = msg_info.Data.local_share_id
        if local_share_id:
            url_get_file = f"{server_file}?app-name={msg_info.AppName}&local-share-id={local_share_id}"
        else:
            token = self.local_api_service.get_access_token("admin/root", "root")
            url_get_file = f"{server_file}?token={token}"

        image_data = self.video_service.get_image(url_get_file)
        image_file_name = f"{pathlib.Path(msg_info.Data['FullFileNameLower']).name}.png"
        # file_path = f'/mnt/files/__gemini_tmp__/{image_file_name}'

        if not os.path.isdir(self.temp_file.get_root_dir()):
            os.makedirs(self.temp_file.get_root_dir(), exist_ok=True)
        server_dir = pathlib.Path(main_file_id.split("://")[1]).parent.__str__().replace(os.sep, '/')
        rel_server_path = os.path.join(server_dir, pathlib.Path(main_file_id).name + ".png").replace(os.sep, '/')
        file_path = os.path.join(self.temp_file.get_root_dir(), str(uuid.uuid4()) + ".png")

        if isinstance(image_data, numpy.ndarray):
            cv2.imwrite(file_path, image_data)
            self.local_api_service.send_file(
                file_path=file_path,
                token=token,
                local_share_id=local_share_id,
                app_name=msg_info.AppName,
                rel_server_path=rel_server_path

            )
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"File '{file_path}' deleted successfully.")
                except PermissionError as e:
                    print(f"Error deleting '{file_path}': {e}")
            else:
                print(f"File '{file_path}' not found.")

            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags["method"].delivery_tag,
                resource=rel_server_path,
                require_tracking=True

            )
            msg.delete(msg_info)
        else:
            msg.delete(msg_info)
        print(msg_info)
