# MSG_FILE_SAVE_OCR_PDF
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

import pymongo
from cyx.common.msg import broker
from cyx.loggers import LoggerService


@broker(message=cyx.common.msg.MSG_FILE_SAVE_OCR_PDF)
class Process:
    def __init__(self, logger=cy_kit.singleton(LoggerService)):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
            from cy_xdoc.services.files import FileServices
            from cy_xdoc.services.search_engine import SearchEngine
            search_engine: SearchEngine = cy_kit.singleton(SearchEngine)
            full_file_path = msg_info.Data['processing_file']
            print(full_file_path)
            file_storage_services = cy_kit.singleton(MongoDbFileService)
            file_services = cy_kit.singleton(FileServices)
            full_file_path = msg_info.Data['processing_file']
            if not os.path.isfile(full_file_path):
                self.logger.info(
                    f"app={msg_info.AppName} save thumb file {full_file_path} was not found msg will be deleted")
                msg.delete(msg_info)
                return
            server_orc_file_path = f'file-ocr/{msg_info.Data["_id"]}/{msg_info.Data["FileNameOnly"]}.pdf'
            fs = None
            try:
                fs = file_storage_services.store_file(
                    app_name=msg_info.AppName,
                    source_file=full_file_path,
                    rel_file_store_path=server_orc_file_path
                )

                self.logger.info(f"app={msg_info.AppName} save thumb file {server_orc_file_path} is OK")
            except pymongo.errors.DuplicateKeyError as e:
                self.logger(e)
                msg.delete(msg_info)
                return

            file_services.update_ocr_info(
                app_name=msg_info.AppName,
                upload_id=msg_info.Data["_id"],
                ocr_file_id=fs.get_id()
            )
            search_engine.update_data_field(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                field_path="data_item.OCRFileId",
                field_value=fs.get_id()
            )
            #
            # file_services.update_main_thumb_id(
            #     app_name=msg_info.AppName,
            #     upload_id=msg_info.Data["_id"],
            #     main_thumb_id=fs.get_id()
            # )
            msg.delete(msg_info)
            self.logger.info(f'update {full_file_path} to ORC of file of {msg_info.Data["_id"]}')
        except Exception as e:
            self.logger.error(e)
