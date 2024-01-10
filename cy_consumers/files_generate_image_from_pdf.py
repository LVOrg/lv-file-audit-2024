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


msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
check={}
@broker(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF)
class Process:
    def __init__(self,
                 content_service=cy_kit.singleton(ContentService),
                 pdf_file_service = cy_kit.singleton(PDFService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger
        self.content_service=content_service
        self.pdf_file_service = pdf_file_service
        self.mongodb_service=mongodb_service




    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        import fitz.fitz
        try:
            print(msg_info)
            resource = self.content_service.get_resource(msg_info)

            img_file = self.pdf_file_service.get_image(resource)
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
        except fitz.fitz.EmptyFileError:
            upload_id = msg_info.Data["_id"]
            doc_context = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
            doc_context.context.update(
                doc_context.fields.id==upload_id,
                doc_context.fields.ThumbnailsAble<<False
            )
            msg.delete(msg_info)
    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            full_file = msg_info.Data.get(cyx.common.msg.PROCESSING_FILE)
            if full_file is None:
                full_file = temp_file.get_path(
                    app_name=msg_info.AppName,
                    file_ext=msg_info.Data["FileExt"],
                    upload_id=msg_info.Data["_id"],
                    file_id=msg_info.Data.get("MainFileId")

                )
            self.logger.info(f"Generate image form {full_file}")
            img_file = self.pdf_file_service.get_image(full_file)
            ret = temp_file.move_file(
                from_file=img_file,
                app_name=msg_info.AppName,
                sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
            )
            msg_info.Data["processing_file"] = ret
        except Exception as e:
            self.logger.error(e)
            msg.delete(msg_info)
            return
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
            data=msg_info.Data
        )
        msg.delete(msg_info)
        self.logger.info(msg_info)