# MSG_FILE_SAVE_OCR_PDF
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading

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

msg = cy_kit.singleton(RabitmqMsg)

content_services = cy_kit.singleton(ContentsServices)
content, info = content_services.get_text(__file__)



from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_utils import texts
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.search_engine import SearchEngine
from cyx.common.temp_file import TempFiles


@broker(message=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine),
                 file_services=cy_kit.singleton(FileServices),
                 temp_file=cy_kit.singleton(TempFiles)
                 ):
        self.logger = logger
        self.search_engine = search_engine
        self.file_services = file_services
        self.temp_file = temp_file

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        pass

    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            full_file_path = msg_info.Data['processing_file']
            if full_file_path is None:
                if (msg_info.Data.get("MainFileId") or "").startswith("local://"):
                    full_file_path = self.temp_file.get_path(
                        app_name=msg_info.AppName,
                        file_ext=msg_info.Data["FileExt"],
                        upload_id=msg_info.Data["_id"],
                        file_id=msg_info.Data.get("MainFileId")
                    )
            if not os.path.isfile(full_file_path):
                self.logger.info(f"{full_file_path} was not found msg was delete")
                msg.delete(msg_info)
                return

            self.logger.info(f"get content from {full_file_path}")
            content, info = content_services.get_text(full_file_path)
            self.logger.info(f"get content from {full_file_path} is ok")
            if content is None:
                self.logger.info(f"get content from{full_file_path} and get no content")
                msg.delete(msg_info)
                return
            content = texts.well_form_text(content)
            upload_item = self.file_services.get_upload_register(
                app_name=msg_info.AppName,
                upload_id=msg_info.Data["_id"]
            )
            self.search_engine.update_content(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                content=content,
                meta_data=None,
                data_item=upload_item
            )

            self.logger.info(f"{full_file_path} was updated to search engine")
            msg.delete(msg_info)
        except Exception as e:
            self.logger.error(e,msg_info= msg_info.Data)
