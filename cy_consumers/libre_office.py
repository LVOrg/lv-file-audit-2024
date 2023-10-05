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


from cyx.common.share_storage import ShareStorageService
# def on_receive_msg(msg_info: MessageInfo):
#     from cyx.media.libre_office import LibreOfficeService
#     full_file = msg_info.Data.get("processing_file")
#     print(full_file)
#
#
# msg.consume(
#     msg_type=cyx.common.msg.MSG_LIBRE_OFFICE_CONVERT_TO_IMAGE,
#     handler=on_receive_msg
# )
from cyx.loggers import LoggerService
from cyx.common.msg import broker


@broker(message=cyx.common.msg.MSG_LIBRE_OFFICE_CONVERT_TO_IMAGE)
class Process:
    def __init__(self,
                 shared_storage_service=cy_kit.singleton(ShareStorageService),
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger
        self.logger.info(f"consumer {cyx.common.msg.MSG_FILE_UPLOAD} init")
        self.temp_file = temp_file

        self.output_dir = shared_storage_service.get_temp_dir(self.__class__)

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        full_file_path = msg_info.Data.get("processing_file")
        self.logger.info(f"msg={self.message_type}, upload_file={full_file_path}")
        """
        Get file from message
        """
        if full_file_path is None:
            """
            Some reason full_file_path could not get . Perhaps the end users remove it from the collection 
            Một số lý do full_file_path không thể nhận được. Có lẽ người dùng cuối xóa nó khỏi bộ sưu tập
            """
            msg.delete(msg_info)
            """
            Eliminate message never occur again
            Loại bỏ tin nhắn không bao giờ xảy ra nữa
            """
            self.logger.info(f"msg={self.message_type}, upload_file={full_file_path},file was not found")
            return

        print(f"{full_file_path} was receive")

        if not os.path.isfile(full_file_path):
            """
                    Some reason file is not exist. Perhaps the end users remove it from the collection 
                    Một số lý do tập tin không tồn tại. Có lẽ người dùng cuối xóa nó khỏi bộ sưu tập
           """

            msg.delete(msg_info)
            print(f"{full_file_path} was not found")
            self.logger.info(f"{full_file_path} was not found")
            return

        print(f"Receive file {full_file_path}")
        self.logger.info(f"Receive file {full_file_path}")
        try:
            print(f"{full_file_path}\n is ok")
        except Exception as e:
            msg.delete(msg_info)
            self.logger.exception(e)
