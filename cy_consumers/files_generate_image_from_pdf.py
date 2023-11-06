#python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_pdf.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
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

import json

temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
@broker(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            full_file = temp_file.get_path(
                app_name=msg_info.AppName,
                file_ext=msg_info.Data["FileExt"],
                upload_id=msg_info.Data["_id"],
                file_id = msg_info.Data.get("MainFileId")

            )
            self.logger.info(f"Generate image form {full_file}")
            img_file = pdf_file_service.get_image(full_file)
            ret = temp_file.move_file(
                from_file=img_file,
                app_name=msg_info.AppName,
                sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
            )
            msg_info.Data["processing_file"] = ret
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data
            )
            msg.delete(msg_info)
            self.logger.info(msg_info)
        except Exception as e:
            self.logger.error(e,msg_info=msg_info.Data)