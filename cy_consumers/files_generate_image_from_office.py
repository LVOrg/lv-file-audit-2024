# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_office.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
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
        try:
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
            if full_file is None:
                self.logger.info(f"Generate image form nothing")
                msg.delete(msg_info)

            self.logger.info(f"Generate image form {full_file}")
            self.logger.info(f"Generate image form {full_file} start")
            img_file = libre_office_service.get_image(file_path=full_file)
            self.logger.info(f"Generate image form {full_file} end")
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
            self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n {full_file}")
            msg.delete(msg_info)
            self.logger.info(msg_info.Data)
        except Exception as e:
            self.logger.error(e,more_info=dict(
                            es_index = msg_info.AppName,
                            data = msg_info.Data
                        ))