# MSG_FILE_SAVE_OCR_PDF
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import uuid

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.media.contents import ContentsServices
from cyx.repository import Repository

msg = cy_kit.singleton(RabitmqMsg)

content_services = cy_kit.singleton(ContentsServices)
content, info = content_services.get_text(__file__)

from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_utils import texts
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.search_engine import SearchEngine
from cyx.content_services import ContentService, ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService

from cyx.local_api_services import LocalAPIService
@broker(message=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 local_api_service=cy_kit.singleton(LocalAPIService)

                 ):
        self.logger = logger
        self.search_engine = search_engine
        self.file_services = mongodb_service
        self.content_service = content_service
        self.mongodb_service = mongodb_service
        self.local_api_service =local_api_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        rel_file_path = msg_info.Data["MainFileId"].split("://")[1]
        print(rel_file_path)
        # phiếu đề xuất mua hàng.docx.search.es
        rel_file_path = f"{rel_file_path}.search.es"
        print(rel_file_path)
        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        content = ""
        with open(server_file, "rb") as fs:
            content = fs.read().decode()
        content = texts.well_form_text(content)
        db_context = Repository.files.app(msg_info.AppName)
        upload_item = db_context.context.find_one(
            db_context.fields.id == msg_info.Data["_id"]
        )

        self.search_engine.update_content(
            app_name=msg_info.AppName,
            id=msg_info.Data["_id"],
            content=content,
            meta_data=None,
            data_item=upload_item
        )

        doc_context = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
        doc_context.context.update(
            doc_context.fields.id == msg_info.Data.get("_id"),
            doc_context.fields.HasSearchContent << True
        )
        msg.delete(msg_info)

    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_resource(msg_info)
        print(msg_info)
        print("---------------------------------")
        print(resource)
        try:
            content = self.get_content(resource)
            self.search_engine.replace_content(
                app_name=msg_info.AppName,
                id=msg_info.Data.get("_id"),
                field_value=content,
                field_path="content"
            )
            doc_context = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
            doc_context.context.update(
                doc_context.fields.id == msg_info.Data.get("_id"),
                doc_context.fields.HasSearchContent << True
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
