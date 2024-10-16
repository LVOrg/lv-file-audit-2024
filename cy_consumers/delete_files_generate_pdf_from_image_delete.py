# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys

import PIL
import img2pdf

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import os.path


import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.temp_file import TempFiles
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService
temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
@broker(cyx.common.msg.MSG_FILE_GENERATE_PDF_FROM_IMAGE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            image_extractor_service = cy_kit.singleton(ImageExtractorService)
            full_file = msg_info.Data.get("processing_file")

            if full_file is None:
                msg.delete(msg_info)
                return
            if not os.path.isfile(full_file):
                if full_file.startswith("/app/"):
                    full_file = os.path.join(working_dir, full_file["/app/".__len__():])
                    if not os.path.isfile(full_file):
                        print(f"Generate pdf from {full_file}:\nfile was not found")
                        msg.delete(msg_info)
                        return
                else:
                    self.logger.info(f"Generate pdf from {full_file}:\nfile was not found")
                    msg.delete(msg_info)
                    return
            self.logger.info(f"Generate image form {full_file}")
            pdf_file = None
            try:
                pdf_file = image_extractor_service.convert_to_pdf(file_path=full_file, file_ext="pdf")
                self.logger.info(f"Generate pdf from {full_file}:\nPDF file is {pdf_file}")
            except PIL.UnidentifiedImageError as e:
                self.logger.error(e,msg_info=msg_info.Data)
                msg.delete(msg_info)

                return
            except img2pdf.AlphaChannelError as e:
                self.logger.error(e,msg_info=msg_info.Data)
                msg.delete(msg_info)
                return

            ret = temp_file.move_file(
                from_file=pdf_file,
                app_name=msg_info.AppName,
                sub_dir=cyx.common.msg.MSG_FILE_GENERATE_PDF_FROM_IMAGE
            )
            msg_info.Data["processing_file"] = ret
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT,
                data=msg_info.Data
            )
            msg.delete(msg_info)
            self.logger.info(f"{cyx.common.msg.MSG_FILE_OCR_CONTENT}\n{ret}:\noriginal file {full_file}")
        except Exception as e:
            self.logger.error(e)