# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_save_custom_thumb.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
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

import json
log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs"

)
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name= pathlib.Path(__file__).stem
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

def on_receive_msg(msg_info: MessageInfo):
    from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
    from cy_xdoc.services.files import FileServices
    file_storage_services = cy_kit.singleton(MongoDbFileService)

    full_file_path = msg_info.Data['processing_file']
    if not os.path.isfile(full_file_path):
        msg.delete(msg_info)
        print(f"File {full_file_path} was not found")
        logs.info(f"File {full_file_path} was not found")
        return

    upload_id = msg_info.Data["_id"]
    print(f"Save {full_file_path} to {upload_id}")
    scale_to_size = pathlib.Path(full_file_path).stem.split('_')[-1:][0]
    file_storage_services.store_file(
        app_name=msg_info.AppName,
        source_file=full_file_path,
        rel_file_store_path=f"thumbs/{upload_id}/{scale_to_size}.webp",
    )
    msg.delete(msg_info)
    logs.info(f"Save {full_file_path} to {upload_id}")


msg.consume(
    msg_type=cyx.common.msg.MSG_FILE_SAVE_CUSTOM_THUMB,
    handler=on_receive_msg
)
