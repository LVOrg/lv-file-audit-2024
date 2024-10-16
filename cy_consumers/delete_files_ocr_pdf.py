# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_ocr_pdf.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
import threading
import time

import ocrmypdf

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
from cyx.media.image_extractor import ImageExtractorService
msg = cy_kit.singleton(RabitmqMsg)
if sys.platform == "linux":
    import signal
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

from cyx.common.msg import broker
from cyx.loggers import LoggerService
@broker(message=cyx.common.msg.MSG_FILE_OCR_CONTENT)
class Process:
    def __init__(self,
                 logger = cy_kit.singleton(LoggerService),
                 temp_file=cy_kit.singleton(TempFiles),
                 pdf_file_service = cy_kit.singleton(PDFService),
                 image_extractor_service = cy_kit.singleton(ImageExtractorService)):
        self.logger = logger
        self.temp_file= temp_file
        self.pdf_file_service = pdf_file_service
        self.image_extractor_service = image_extractor_service
    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        if msg_info.Data.get("processing_file"):
            full_file = msg_info.Data["processing_file"]
        try_count=5
        while try_count>0:
                self.logger.info(f'Try pull file {msg_info.Data["_id"]},{msg_info.Data["FileExt"]} in {msg_info.AppName}')
                full_file = self.temp_file.get_path(
                    app_name=msg_info.AppName,
                    file_ext=msg_info.Data["FileExt"],
                    upload_id=msg_info.Data["_id"],
                    file_id=msg_info.Data.get("MainFileId")
                )
                if not os.path.isfile(full_file):
                    time.sleep(10)
                    try_count -=1
                else:
                    try_count =0



        if not os.path.isfile(full_file):
            self.logger.info(f"{full_file} was not found")
            msg.delete(msg_info)
            return
        else:
            self.logger.info(f"{full_file} is ok")

        def th_run(full_file, msg, msg_info):
            ocr_file = None
            self.logger.info(f"Do OCR file {full_file}")
            try:
                ocr_file = self.pdf_file_service.ocr(
                    pdf_file=full_file,

                )
                self.logger.info(f"Do OCR file {full_file} is ok:\n{ocr_file}")

            except ocrmypdf.exceptions.InputFileError as e:
                self.logger.error(e,more_info=msg_info.Data)
                msg.delete(msg_info)
                msg_info.Data["processing_file"] = full_file
            except Exception as e:
                self.logger.error(e, more_info =msg_info.Data)
                msg.delete(msg_info)
                msg_info.Data["processing_file"] = full_file
            if not isinstance(msg_info.Data.get("MainFileId"),str) or not msg_info.Data["MainFileId"].startswith("local://"):
                ret = self.temp_file.move_file(
                    from_file=ocr_file,
                    app_name=msg_info.AppName,
                    sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
                )
                msg_info.Data["processing_file"] = ret
                self.logger.info(f"output file is {ret}")
            else:
                msg_info.Data["processing_file"]=ocr_file
            msg.delete(msg_info)
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_SAVE_OCR_PDF,
                data=msg_info.Data
            )
            self.logger.info(f"{cyx.common.msg.MSG_FILE_SAVE_OCR_PDF}\n {ocr_file or full_file}\n Original File {full_file}")
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE,
                data=msg_info.Data
            )
            self.logger.info(f"{cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE}\n {ret}\n Original File {full_file}")

            del msg_info
            cy_kit.clean_up()
        th_run(full_file, msg, msg_info)