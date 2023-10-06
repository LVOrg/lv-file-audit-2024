# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_video.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
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
@broker(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            from cyx.common.temp_file import TempFiles

            temp_file = cy_kit.singleton(TempFiles)
            video_service = cy_kit.singleton(VideoServices)
            full_file = msg_info.Data.get("processing_file")
            if full_file is None:
                msg.delete(msg_info)
                return
            img_file = None
            try:
                img_file = video_service.get_image(full_file)
                self.logger.info(f"Generate image from {full_file} was complete at:\n {img_file}")
            except Exception as e:
                self.logger.error(e,msg_info=msg_info.Data)
                msg.delete(msg_info)
                return
            ret = temp_file.move_file(
                from_file=img_file,
                app_name=msg_info.AppName,
                sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO
            )

            self.logger.info(f"Generate image from {full_file} was complete at:\n {ret}")
            msg_info.Data["processing_file"] = ret
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data
            )

            self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n{ret}\nOriginal file:\n{full_file}")

            pdf_file = video_service.get_pdf(full_file, num_of_segment=60)
            pdf_file = temp_file.move_file(
                from_file=pdf_file,
                app_name=msg_info.AppName,
                sub_dir=cyx.common.msg.MSG_FILE_OCR_CONTENT
            )
            msg_info.Data["processing_file"] = pdf_file
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT,
                data=msg_info.Data
            )
            self.logger.info(f"{cyx.common.msg.MSG_FILE_OCR_CONTENT}\n{ret}\nOriginal file:\n{full_file}")
            os.remove(full_file)
        except Exception as e:
            self.logger.error(e)


