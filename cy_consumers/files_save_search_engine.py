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
import json

log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs"

)
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)
if isinstance(config.get('rabbitmq'), dict):
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=RabitmqMsg
    )
else:
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=Broker
    )
msg = cy_kit.singleton(MessageService)

content_services = cy_kit.singleton(ContentsServices)
content, info = content_services.get_text(__file__)


def on_receive_msg(msg_info: MessageInfo):
    # try:
    from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
    try:
        from cy_xdoc.services.files import FileServices
        from cy_xdoc.services.search_engine import SearchEngine
        search_engine: SearchEngine = cy_kit.singleton(SearchEngine)
        file_services = cy_kit.singleton(FileServices)

        full_file_path = msg_info.Data['processing_file']
        if not os.path.isfile(full_file_path):
            logs.info(f"{full_file_path} was not found")
            print(f"{full_file_path} was not found")
            msg.delete(msg_info)
            return

        print(f"get content from {full_file_path}")
        logs.info(f"get content from {full_file_path}")
        content, info = content_services.get_text(full_file_path)
        print(f"get content from {full_file_path} is ok")
        logs.info(f"get content from {full_file_path} is ok")
        if content is None:
            print(f"get content from{full_file_path} and get no content")
            logs.info(f"get content from{full_file_path} and get no content")
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
        print(f"{full_file_path} was updated to search engine")
        logs.info(f"{full_file_path} was updated to search engine")
        msg.delete(msg_info)
    except Exception as e:
        logs.info(e)
        print(e)


msg.consume(
    msg_type=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE,
    handler=on_receive_msg
)
