# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_video.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
from datetime import time

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
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
@broker(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 temp_file=cy_kit.singleton(TempFiles),
                 video_service=cy_kit.singleton(VideoServices),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 ):
        self.logger = logger
        self.temp_file=temp_file
        self.video_service = video_service
        self.content_service=content_service
        self.mongodb_service=mongodb_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_resource(msg_info)
        docs = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
        if resource is None:
            msg.delete(msg_info)
            return
        if not os.path.isfile(resource):
            docs.context.update(
                docs.fields.id==msg_info.Data["_id"],
                docs.fields.ThumbnailsAble<<False
            )
            msg.delete(msg_info)
            return
        img_file = self.video_service.get_image(resource)
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
            data=msg_info.Data,
            parent_msg=msg_info.MsgType,
            parent_tag=msg_info.tags["method"].delivery_tag,
            resource=img_file,
            require_tracking=True

        )
        msg.delete(msg_info)

        print(msg_info)
    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        from cyx.common.temp_file import TempFiles

        full_file = msg_info.Data.get("processing_file")
        try_count = 5
        while try_count > 0 and not os.path.isfile(full_file):
            self.logger.info(
                f'Try pull file {msg_info.Data["_id"]},{msg_info.Data["FileExt"]} in {msg_info.AppName}')
            full_file = self.temp_file.get_path(
                app_name=msg_info.AppName,
                file_ext=msg_info.Data["FileExt"],
                upload_id=msg_info.Data["_id"],
                file_id=msg_info.Data.get("MainFileId")
            )
            if not os.path.isfile(full_file):
                time.sleep(10)
                try_count -= 1
            else:
                try_count = 0
        if full_file is None:
            msg.delete(msg_info)
            return
        img_file = None
        try:
            img_file = self.video_service.get_image(full_file)
            self.logger.info(f"Generate image from {full_file} was complete at:\n {img_file}")
        except Exception as e:
            self.logger.error(e, msg_info=msg_info.Data)
            msg.delete(msg_info)
            return
        # ret = temp_file.move_file(
        #     from_file=img_file,
        #     app_name=msg_info.AppName,
        #     sub_dir=f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO}/{pathlib.Path(full_file).parent.name}"
        # )

        self.logger.info(f"Generate image from {img_file} was complete")
        msg_info.Data["processing_file"] = img_file
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
            data=msg_info.Data
        )

        # self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n{ret}\nOriginal file:\n{full_file}")

        # pdf_file = self.video_service.get_pdf(full_file, num_of_segment=60)
        # pdf_file = temp_file.move_file(
        #     from_file=pdf_file,
        #     app_name=msg_info.AppName,
        #     sub_dir=cyx.common.msg.MSG_FILE_OCR_CONTENT
        # )
        # msg_info.Data["processing_file"] = pdf_file
        # msg.emit(
        #     app_name=msg_info.AppName,
        #     message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT,
        #     data=msg_info.Data
        # )
        # self.logger.info(f"{cyx.common.msg.MSG_FILE_OCR_CONTENT}\n{ret}\nOriginal file:\n{full_file}")
        if isinstance(msg_info.Data.get("MainFileId"), str) and msg_info.Data["MainFileId"].startswith("local://"):
            pass
        else:
            os.remove(full_file)
        self.logger.info(msg_info.Data)
        msg.delete(msg_info)



