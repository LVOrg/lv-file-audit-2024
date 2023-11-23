import datetime
import pathlib



WORKING_DIR = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(WORKING_DIR)
import cy_kit
from cyx.common.msg import (
    broker,
    MSG_APP_RE_INDEX_ALL,
    MSG_FILE_UPLOAD,
    MessageInfo,
    MessageService
)
from cyx.loggers import LoggerService
from cy_xdoc.services.files import FileServices
import cy_docs

@broker(message=MSG_APP_RE_INDEX_ALL)
class Consumer:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 files_service = cy_kit.singleton(FileServices)
                 ):
        print(f"{MSG_APP_RE_INDEX_ALL} is init")
        self.logger = logger
        self.files_service = files_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            txt_msg = f"{MSG_APP_RE_INDEX_ALL} receive message from app {msg_info.AppName} at time {msg_info.CreatedOn}"
            self.logger.info(txt_msg)
            qr = self.files_service.get_queryable_doc(msg_info.AppName)
            is_continue = True
            while is_continue:
                filer_file = cy_docs.EXPR(qr.fields.SizeInBytes == qr.fields.SizeUploaded)
                process_time = datetime.datetime.utcnow()
                process_field= f"{process_time.year}_{process_time.month: 02}_{process_time.day :02}_{process_time.minute: 02}"

                fileter_reindex = cy_docs.not_exists(getattr(cy_docs.fields.ReIndexInfo,process_field))
                try:
                    items = qr.context.aggregate().match(
                        filer_file|fileter_reindex
                    ).sort(
                        qr.fields.RegisterOn.desc()
                    ).limit(100)
                    items_list = list(items)
                    is_continue = len(items_list)>0
                    for x in items:
                        txt_msg = f"{msg_info.AppName}\t{x[qr.fields.FileName]} re-index content with {MSG_FILE_UPLOAD}"
                        try:

                            self.logger.info(txt_msg)
                            msg_broker.emit(
                                app_name= msg_info.AppName,
                                message_type=MSG_FILE_UPLOAD,
                                data=x
                            )
                            qr.context.update(
                                qr.fields.id == x.id,
                                getattr(cy_docs.fields.ReIndexInfo,process_field)<<True
                            )
                            msg_broker.delete(msg_info)
                        except Exception as e:
                            self.logger.error(e)
                except Exception as e:
                    self.logger.error(e)
            print("Run")
        except Exception as e:
            self.logger.error(e)
            msg_broker.delete(msg_info)