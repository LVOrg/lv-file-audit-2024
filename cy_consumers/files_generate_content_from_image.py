# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import subprocess
import sys
import time
import uuid

import requests

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
from cyx.socat_services import SocatClientService
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
from cyx.lv_ocr_services import LVOCRService
from cy_utils import texts
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_IMAGE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 os_command_service=cy_kit.singleton(OSCommandService),
                 socat_client_service = cy_kit.singleton(SocatClientService),
                 lv_ocr_service = cy_kit.singleton(LVOCRService),
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine)

                 ):
        self.logger = logger

        self.local_api_service = local_api_service

        self.os_command_service = os_command_service
        self.socat_client_service = socat_client_service
        self.lv_ocr_service = lv_ocr_service
        # self.socat_client_service.start(8765)
        self.search_engine = search_engine
        print("OK")

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        rel_file_path = None
        try:
            rel_file_path: str = msg_info.Data["MainFileId"].split("://")[1]
        except:
            msg.delete(msg_info)
            return
        self.logger.info(f"process file {rel_file_path} ...")
        print(f"process file {rel_file_path} ...")
        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        # es_server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path+".search.es"
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        file_ext = pathlib.Path(rel_file_path).suffix
        download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
        try:
            with open(server_file, "rb") as fs:
                with open(download_file_path, "wb") as ft:
                    ft.write(fs.read())
        except requests.exceptions.HTTPError as ex:
            self.logger.error(ex)
            if ex.response.status_code in [404,500]:
                msg.delete(msg_info)
                return
        try:
            self.logger.info(f"call lv service {self.lv_ocr_service.url}")

            text = self.lv_ocr_service.do_orc(download_file_path)
            content = texts.well_form_text(text)
            db_context = Repository.files.app(msg_info.AppName)
            upload_item = db_context.context.find_one(
                db_context.fields.id == msg_info.Data["_id"]
            )

            self.search_engine.update_content(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                content=content,
                meta_data=None,
                data_item=upload_item
            )
            db_context.context.update(
                db_context.fields.id == msg_info.Data["_id"],
                db_context.fields.HasORCContent<<True
            )
            os.remove(download_file_path)
            msg.delete(msg_info)
            print(f"process file {rel_file_path} is complete")
        except Exception as e:
            self.logger.error(e)
            print(f"process file {rel_file_path} is error")

    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        self.socat_client_service.send_command("echo ok",8765)
    def on_receive_msg_old(self, msg_info: MessageInfo, msg_broker: MessageService):

        rel_file_path: str = msg_info.Data["MainFileId"].split("://")[1]
        print(f"process file {rel_file_path}")
        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        # es_server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path+".search.es"
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        file_ext = pathlib.Path(rel_file_path).suffix
        download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
        try:
            with open(server_file, "rb") as fs:
                with open(download_file_path, "wb") as ft:
                    ft.write(fs.read())
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code in [404,500]:
                msg.delete(msg_info)
                return


        source = os.path.join(working_dir, "cy-commands", "sender.sh")
        if not os.path.isfile(download_file_path):
            msg.delete(msg_info)
            return
        ocr_command = f"python3.9 /cmd/ocr.py /tmp-files/{pathlib.Path(download_file_path).name}"
        ret = self.socat_client_service.send(ocr_command)
        print(ret)

        text_file = f'/tmp-files/{pathlib.Path(download_file_path).name}.txt'
        log_file = f'/tmp-files/{pathlib.Path(download_file_path).name}.log.txt'
        if not os.path.isfile(text_file) :
            text_file = f"{download_file_path}.txt"
        count = 5
        print("process ...")
        while not os.path.isfile(text_file) and not os.path.isfile(log_file):
            time.sleep(2)

        if os.path.isfile(log_file):
            with open(log_file,"rb") as fs:
                print(fs.read())
            os.remove(download_file_path)
            msg.delete(msg_info)
            return
        if os.path.isfile(text_file):
            self.local_api_service.send_file(
                file_path=text_file,
                token=token,
                local_share_id=local_share_id,
                app_name=msg_info.AppName,
                rel_server_path=rel_file_path + ".search.es"

            )
            msg.emit_child_message(
                parent_message=msg_info,
                message_type=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT,
                resource=rel_file_path + ".search.es"
            )
            os.remove(text_file)
            os.remove(download_file_path)
            msg.delete(msg_info)

        else:
            print(f"can not process file {rel_file_path}")
            os.remove(download_file_path)
            msg.delete(msg_info)

        print(f"process file {rel_file_path} xong, tiep")

            # msg.delete(msg_info)
        # chmod o+rx /home/vmadmin/python/cy-py/tmp-files/838ccca1-24d4-468e-a8b0-7a902f0bc0de.png
