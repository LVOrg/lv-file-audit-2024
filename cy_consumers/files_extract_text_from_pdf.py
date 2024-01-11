import pathlib
import shutil
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cyx.framewwork_configs

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common import config
from cyx.common.rabitmq_message import RabitmqMsg
msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import  LoggerService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.media.contents import ContentsServices
import os
__check_id__ ={}
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_PDF)
class Process:
    def __init__(self,
                 file_services = cy_kit.singleton(FileServices),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 extract_text_service= cy_kit.singleton(ContentsServices),
                 logger = cy_kit.singleton(LoggerService)
                 ):
        self.file_services = file_services
        self.extract_text_service=extract_text_service
        self.content_service= content_service
        self.logger = logger
        self.mongodb_service= mongodb_service


    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_master_resource(msg_info)
        docs = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
        upload_id= msg_info.Data.get("_id")
        print(msg_info)
        print("----------------------------")
        print(resource)
        text,meta = self.extract_text_service.get_text(resource)
        text= self.content_service.well_form_text(text)
        if text=="":
            docs.context.update(
                docs.fields.id==upload_id,
                docs.fields.IsRequireOCR<<True,
                docs.fields.DocType<<"Pdf",
                docs.fields.SearchContentAble<<True,
                docs.fields.HasSearchContent<<False
            )
            msg.emit_child_message(
                parent_message=msg_info,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT_FROM_PDF,
                resource=resource
            )
            msg.delete(msg_info)
        else:
            child_resource = self.content_service.create_content_file(master_resource=resource, content=text)
            msg.emit_child_message(
                parent_message=msg_info,
                message_type=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT,
                resource=child_resource
            )
            msg.delete(msg_info)



