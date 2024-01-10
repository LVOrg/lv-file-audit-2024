# MSG_FILE_SAVE_OCR_PDF
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading

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
from cyx.media.contents import ContentsServices

msg = cy_kit.singleton(RabitmqMsg)

content_services = cy_kit.singleton(ContentsServices)
content, info = content_services.get_text(__file__)



from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_utils import texts
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.search_engine import SearchEngine
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService

@broker(message=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine),
                 content_service= cy_kit.singleton(ContentService),
                 mongodb_service = cy_kit.singleton(MongodbService)

                 ):
        self.logger = logger
        self.search_engine = search_engine
        self.file_services = mongodb_service
        self.content_service = content_service
        self.mongodb_service=mongodb_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_resource(msg_info)
        print(msg_info)
        print("---------------------------------")
        print(resource)
        try:
            content= self.get_content(resource)
            self.search_engine.replace_content(
                app_name=msg_info.AppName,
                id= msg_info.Data.get("_id"),
                field_value= content,
                field_path="content"
            )
            doc_context= self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
            doc_context.context.update(
                doc_context.fields.id==msg_info.Data.get("_id"),
                doc_context.fields.HasSearchContent<<True
            )
            msg.delete(msg_info)
        except FileNotFoundError:
            msg.delete(msg_info)
        except Exception as e:
            print(e)

    def get_content(self, resource):
        with open(resource, "rb") as fs:
            content = fs.read()
            return content.decode('utf8')


