import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import os.path
import pathlib
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
temp_file = cy_kit.singleton(TempFiles)

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
log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs"

)
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)



def on_receive_msg(msg_info: MessageInfo):
    from cyx.media.libre_office import LibreOfficeService
    full_file = msg_info.Data.get("processing_file")
    print(full_file)

print("OK")
