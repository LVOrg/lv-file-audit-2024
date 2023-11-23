# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
import time

import PIL
import img2pdf

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
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
from cyx.easy_ocr import EasyOCRService

temp_file = cy_kit.singleton(TempFiles)


msg = cy_kit.singleton(RabitmqMsg)







# msg.consume(
#     msg_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
#     handler=on_receive_msg
# )
from cyx.common.msg import broker
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.files import FileServices
from cyx.loggers import LoggerService
import elasticsearch.exceptions
@broker(message=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE)
class Process:
    def __init__(self,
                 easy_service=cy_kit.singleton(EasyOCRService),
                 file_services = cy_kit.singleton(FileServices),
                 search_engine = cy_kit.singleton(SearchEngine),
                 logger = cy_kit.singleton(LoggerService),
                 temp_file=cy_kit.singleton(TempFiles)
    ):
        self.easy_service = easy_service
        self.file_services = file_services
        self.search_engine = search_engine
        self.logger = logger
        self.temp_file= temp_file

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        full_file = msg_info.Data.get("processing_file")
        if not os.path.isfile(full_file):
            full_file = self.temp_file.get_path(
                app_name=msg_info.AppName,
                file_ext=msg_info.Data["FileExt"],
                upload_id=msg_info.Data["_id"],
                file_id=msg_info.Data.get("MainFileId")
            )
        if full_file is None:
            msg.delete(msg_info)
            return

        if not os.path.isfile(full_file):

            if full_file is None:
                msg.delete(msg_info)
                self.logger.info(f"Generate pdf from {full_file}:\nfile was not found")
                return
        upload_item = self.file_services.get_upload_register(
            app_name=msg_info.AppName,
            upload_id=msg_info.Data["_id"]
        )
        if upload_item:
            if not os.path.isfile(full_file):
                msg.delete(msg_info)
                return
            content = self.easy_service.get_text(image_file=full_file)
            if content == "":
                msg.delete(msg_info)
                return
            self.search_engine.update_content(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                content=content,
                data_item=upload_item
            )
            # self.logger.info(f"Generate pdf from {full_file}:\nPDF file is {pdf_file}")
            msg.delete(msg_info)