# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys

import PIL
import img2pdf

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
from cyx.easy_ocr import EasyOCRService

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
    from cy_xdoc.services.search_engine import SearchEngine
    from cy_xdoc.services.files import FileServices
    easy_service = cy_kit.singleton(EasyOCRService)
    file_services = cy_kit.singleton(FileServices)
    search_engine = cy_kit.singleton(SearchEngine)
    full_file = msg_info.Data.get("processing_file")
    if full_file is None:
        msg.delete(msg_info)
        return
    if not os.path.isfile(full_file):
        # full_file = temp_file.get_path(
        #     app_name=msg_info.AppName,
        #     file_ext=msg_info.Data["FileExt"],
        #     upload_id=msg_info.Data["_id"]
        # )
        if full_file is None:
            msg.delete(msg_info)
            print(f"Generate pdf from {full_file}:\nfile was not found")
            return
    print(f"Generate image form {full_file}")
    pdf_file = None
    try:

        upload_item = file_services.get_upload_register(
            app_name=msg_info.AppName,
            upload_id=msg_info.Data["_id"]
        )
        if upload_item:
            if not os.path.isfile(full_file):
                msg.delete(msg_info)
                return
            content = easy_service.get_text(image_file=full_file)
            if content == "":
                msg.delete(msg_info)
                return
            try:
                search_engine.update_content(
                    app_name=msg_info.AppName,
                    id=msg_info.Data["_id"],
                    content=content,
                    data_item=upload_item
                )
            except Exception as e:
                print(f"{__file__} search_engine.update_content is error")
                print(e)
            print(f"Generate pdf from {full_file}:\nPDF file is {pdf_file}")
            logs.info(f"Generate pdf from {full_file}:\nPDF file is {pdf_file}")
            msg.delete(msg_info)

    except img2pdf.AlphaChannelError as e:
        logs.exception(e)
        msg.delete(msg_info)
        print(f"Generate pdf from {full_file} is error:\n")
        print(e)
        return


msg.consume(
    msg_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
    handler=on_receive_msg
)
