# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_office.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
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
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

import json

temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)
image_extractor_service = cy_kit.singleton(ImageExtractorService)
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
import fitz
print(fitz.version)
def on_receive_msg(msg_info: MessageInfo):
    from cyx.media.libre_office import LibreOfficeService
    libre_office_service = cy_kit.singleton(LibreOfficeService)
    if msg_info.Data["FileExt"] == "pdf":
        msg.delete(msg_info)
        return
    full_file = temp_file.get_path(
        app_name=msg_info.AppName,
        file_ext=msg_info.Data["FileExt"],
        upload_id=msg_info.Data["_id"]

    )
    print(f"Generate image form {full_file}")
    print(f"Generate image form {full_file} start")
    img_file = libre_office_service.get_image(file_path=full_file)
    print(f"Generate image form {full_file} end")
    ret = temp_file.move_file(
        from_file=img_file,
        app_name=msg_info.AppName,
        sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
    )
    msg_info.Data["processing_file"] = ret
    msg.emit(
        app_name=msg_info.AppName,
        message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
        data=msg_info.Data
    )
    print(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n {full_file}")
    msg.delete(msg_info)
    logs.info(msg_info)


if sys.platform == "linux":
    import signal

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
msg.consume(
    msg_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
    handler=on_receive_msg
)
