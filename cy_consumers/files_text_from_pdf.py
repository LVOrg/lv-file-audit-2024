import os
import pathlib
import sys
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

import pymongo
from cyx.common.msg import broker
from cyx.loggers import LoggerService

from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.files import FileServices
@broker(message=cyx.common.msg.MSG_FILE_OCR_CONTENT)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 temp_file=cy_kit.singleton(TempFiles),
                 pdf_file_service=cy_kit.singleton(PDFService),
                 image_extractor_service=cy_kit.singleton(ImageExtractorService),
                 search_engine = cy_kit.singleton(SearchEngine),
                 file_services = cy_kit.singleton(FileServices)):
        self.logger = logger
        self.temp_file = temp_file
        self.pdf_file_service = pdf_file_service
        self.image_extractor_service = image_extractor_service
        self.search_engine = search_engine
        self.file_services = file_services
        self.try_count_dict ={}

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        full_file = self.temp_file.get_path(
            app_name=msg_info.AppName,
            file_ext=msg_info.Data["FileExt"],
            upload_id=msg_info.Data["_id"],
            file_id=msg_info.Data.get("MainFileId")
        )
        if not os.path.isfile(full_file):
            msg_broker.delete(msg_info)
        try_count = 3
        while try_count>0:
            try:
                text = self.pdf_file_service.ocr_text(full_file)
                upload_item = self.file_services.get_upload_register(
                    app_name=msg_info.AppName,
                    upload_id=msg_info.Data["_id"]
                )
                self.search_engine.update_content(
                    app_name=msg_info.AppName,
                    id=msg_info.Data["_id"],
                    content=text,
                    meta_data= {},
                    data_item=upload_item
                )
                self.logger.info(f"{full_file} was updated to search engine")
                try_count =0
            except:
                time.sleep(2)
                try_count-=1
        msg_broker.delete(msg_info)





"""
rabbitmq:
  port_: 31674
  server: 172.16.7.99
  port: 31674
  msg: v99-dev
"""

