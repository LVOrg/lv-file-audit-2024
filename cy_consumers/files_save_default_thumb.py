# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cyx.framewwork_configs
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
__check__  = {}
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
            upload_id = msg_info.Data.get("_id") or msg_info.Data.get("UploadId")
            print(upload_id)


            check = self.file_services.get_msg_check_list(
                app_name=msg_info.AppName,
                upload_id = upload_id,
                key=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB
            )
            if check !=0:
                msg.delete(msg_info)
                return
            else:
                self.file_services.update_msg_check_list(
                    app_name=msg_info.AppName,
                    upload_id=upload_id,
                    key=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                    value=2
                )
            full_file_path = msg_info.Data['processing_file']
            fs = self.file_storage_services.store_file(
                app_name=msg_info.AppName,
                source_file=full_file_path,
                rel_file_store_path=f"thumb/{msg_info.Data['FullFileName'].lower()}.webp",
            )
            check_path = os.path.join(config.file_storage_path, fs.get_id().split("://")[1])
            if not os.path.isfile(check_path):
                msg.emit(
                    app_name=msg_info.AppName,
                    message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                    data=self.file_services.get_upload_register(
                        app_name=msg_info.AppName,
                        upload_id=upload_id
                    )

                )
                msg.delete(msg_info)
                return

            self.file_services.update_main_thumb_id(
                app_name=msg_info.AppName,
                upload_id=upload_id,
                main_thumb_id=fs.get_id()
            )

            self.search_engine.update_data_field(
                app_name=msg_info.AppName,
                id=upload_id,
                field_path="data_item.HasThumb",
                field_value=True
            )
            msg.delete(msg_info)
            self.logger.info(f"update {check_path} to thumb of file")
            self.file_services.update_msg_check_list(
                app_name=msg_info.AppName,
                upload_id=upload_id,
                key=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                value=2
            )
        except FileNotFoundError:
            msg.emit(
                app_name=msg_info.AppName,
                message_type= cyx.common.msg.MSG_FILE_UPLOAD,
                data= self.file_services.get_upload_register(
                    app_name=msg_info.AppName,
                    upload_id = upload_id
                )

            )
            msg.delete(msg_info)
