# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import subprocess
import sys
import time
import uuid

import PIL
import img2pdf

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import os.path
import pathlib

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
from cyx.os_command_services import OSCommandService





msg = cy_kit.singleton(RabitmqMsg)







# msg.consume(
#     msg_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
#     handler=on_receive_msg
# )
from cyx.common.msg import broker
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.files import FileServices
from cyx.loggers import LoggerService
import elasticsearch.exceptions
from cyx.repository import Repository
from cyx.local_api_services import LocalAPIService
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_IMAGE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 os_command_service = cy_kit.singleton(OSCommandService)

                 ):
        self.logger = logger

        self.local_api_service = local_api_service

        self.os_command_service = os_command_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):

        rel_file_path: str = msg_info.Data["MainFileId"].split("://")[1]

        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        file_ext = pathlib.Path(rel_file_path).suffix
        download_file_path = os.path.join(working_dir,"tmp-files",str(uuid.uuid4())+file_ext)
        with open(server_file,"rb") as fs:
            with open(download_file_path,"wb") as ft:
                ft.write(fs.read())
        source = os.path.join(working_dir,"cy-commands","sender.sh")
        if os.path.isfile("/cmd/sender.sh"):
            source = "/cmd/sender.sh"
        ocr_command = f"\"python3.9 /cmd/ocr.py '/tmp-files/{pathlib.Path(download_file_path).name}'\""

        txt = self.os_command_service.execute_command_with_polling([
            source,
            "ocr", ocr_command
        ])
        print(txt)
        #chmod o+rx /home/vmadmin/python/cy-py/tmp-files/838ccca1-24d4-468e-a8b0-7a902f0bc0de.png

