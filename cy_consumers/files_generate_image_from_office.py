# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_office.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import os.path
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)
msg = cy_kit.singleton(RabitmqMsg)


if sys.platform == "linux":
    import signal

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

from cyx.common.msg import broker
from cyx.loggers import LoggerService


@broker(message=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        from cyx.media.libre_office import LibreOfficeService
        libre_office_service = cy_kit.singleton(LibreOfficeService)
        ext_file = msg_info.Data.get("FileExt")
        if ext_file is None:
            ext_file = pathlib.Path(msg_info.Data["FileName"]).suffix
            if ext_file:
                ext_file = ext_file[1:].lower()
        if ext_file == "pdf":
            msg.delete(msg_info)
            return
        full_file = msg_info.Data.get("processing_file")
        if not full_file:
            if isinstance(msg_info.Data.get("MainFileId"),str):
                full_file = os.path.join(cyx.common.config.file_storage_path, msg_info.Data.get("MainFileId").split("://")[1])
                if not os.path.isfile(full_file):
                    full_file = None
        if not full_file:
            full_file = temp_file.get_path(
                app_name=msg_info.AppName,
                file_ext=msg_info.Data["FileExt"],
                upload_id=msg_info.Data["_id"],
                file_id=msg_info.Data.get("MainFileId")

            )
        if full_file is None:
            self.logger.info(f"Generate image form nothing")
            msg.delete(msg_info)
            return
        if not os.path.isfile(full_file):
            self.logger.info(f"Generate image form nothing")
            msg.delete(msg_info)
            return

        self.logger.info(f"Generate image form {full_file}")
        self.logger.info(f"Generate image form {full_file} start")
        img_file = libre_office_service.get_image(file_path=full_file)
        self.logger.info(f"Generate image form {full_file} end")
        # ret = temp_file.move_file(
        #     from_file=img_file,
        #     app_name=msg_info.AppName,
        #     sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
        # )
        msg_info.Data["processing_file"] = img_file
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
            data=msg_info.Data
        )
        self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n {full_file}")
        msg.delete(msg_info)
        self.logger.info(msg_info.Data)