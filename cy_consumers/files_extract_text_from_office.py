import pathlib
import shutil
import sys
import uuid

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cy_file_cryptor.wrappers
import cyx.framewwork_configs

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common import config
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

from cyx.common.rabitmq_message import RabitmqMsg
msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import  LoggerService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.media.contents import ContentsServices
import urllib.parse
from cyx.local_api_services import LocalAPIService
from cyx.common.temp_file import TempFiles
import os
__check_id__ ={}
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_OFFICE)
class Process:
    def __init__(self,
                 file_services = cy_kit.singleton(FileServices),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 extract_text_service= cy_kit.singleton(ContentsServices),
                 logger = cy_kit.singleton(LoggerService),
                 local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService),
                 temp_file=cy_kit.singleton(TempFiles),
                 ):
        self.file_services = file_services
        self.extract_text_service=extract_text_service
        self.content_service= content_service
        self.logger = logger
        self.mongodb_service= mongodb_service
        self.local_api_service=local_api_service
        self.temp_file=temp_file

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        rel_file_path = msg_info.Data["MainFileId"].split("://")[1]
        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        download_file = os.path.join(self.temp_file.get_root_dir(), str(uuid.uuid4()))
        with open(server_file,"rb") as fs:
            with open(download_file,"wb") as fd:
                fd.write(fs.read())

        text, meta = self.extract_text_service.get_text(download_file)
        search_content_file=f"{rel_file_path}.search.es"
        file_path = os.path.join(self.temp_file.get_root_dir(), str(uuid.uuid4()))
        with open(file_path, "wb") as f:
            f.write(text.encode())
        self.local_api_service.send_file(
            file_path=file_path,
            token=token,
            local_share_id=local_share_id,
            app_name=msg_info.AppName,
            rel_server_path=search_content_file

        )
        msg.emit_child_message(
            parent_message=msg_info,
            message_type=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT,
            resource=search_content_file
        )
        os.remove(file_path)
        os.remove(download_file)
        msg.delete(msg_info)
    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_master_resource(msg_info)
        print(msg_info)
        print("----------------------------")
        print(resource)
        text,meta = self.extract_text_service.get_text(resource)
        text= self.content_service.well_form_text(text)
        child_resource= self.content_service.create_content_file(master_resource=resource,content=text)
        msg.emit_child_message(
            parent_message= msg_info,
            message_type=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT,
            resource= child_resource
        )
        msg.delete(msg_info)