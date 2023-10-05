# MSG_FILE_SAVE_OCR_PDF
# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_default_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
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


@broker(message=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE)
class Process:
    def __init__(self, logger=cy_kit.singleton(LoggerService)):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            from cy_xdoc.services.files import FileServices
            from cy_xdoc.services.search_engine import SearchEngine
            search_engine: SearchEngine = cy_kit.singleton(SearchEngine)
            file_services = cy_kit.singleton(FileServices)

            full_file_path = msg_info.Data['processing_file']
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

            upload_item = file_services.get_upload_register(
                app_name=msg_info.AppName,
                upload_id=msg_info.Data["_id"]
            )
            search_engine.update_content(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                content=content,
                meta_data=info,
                data_item=upload_item
            )

            self.logger.info(f"{full_file_path} was updated to search engine")
            msg.delete(msg_info)
        except Exception as e:
            self.logger.error(e)
