# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config

msg = cy_kit.singleton(RabitmqMsg)

from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService
from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.search_engine import SearchEngine
from cyx.loggers import LoggerService

@broker(message=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB)
class Process:
    def __init__(self,
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine),
                 file_storage_services=cy_kit.singleton(MongoDbFileService),
                 file_services=cy_kit.singleton(FileServices),
                 logger = cy_kit.singleton(LoggerService)
                 ):
        self.search_engine = search_engine
        self.file_storage_services = file_storage_services
        self.file_services = file_services
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            full_file_path = msg_info.Data['processing_file']
            fs = self.file_storage_services.store_file(
                app_name=msg_info.AppName,
                source_file=full_file_path,
                rel_file_store_path=f"thumb/{msg_info.Data['FullFileNameLower']}.webp",
            )

            self.file_services.update_main_thumb_id(
                app_name=msg_info.AppName,
                upload_id=msg_info.Data["_id"],
                main_thumb_id=fs.get_id()
            )

            self.search_engine.update_data_field(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                field_path="data_item.HasThumb",
                field_value=True
            )
            msg.delete(msg_info)
            self.logger.info(f"update {full_file_path} to thumb of file")
        except Exception as e:
            self.logger.error(e,msg_info=msg_info.Data)
