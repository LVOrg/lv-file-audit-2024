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
from cyx.common import config
@broker(message=MSG_APP_RE_INDEX_ALL,allow_resume=True)
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
            msg_broker.delete(msg_info)
            txt_msg = f"{MSG_APP_RE_INDEX_ALL} receive message from app {msg_info.AppName} at time {msg_info.CreatedOn}"
            self.logger.info(txt_msg)
            qr = self.files_service.get_queryable_doc(msg_info.AppName)
            is_continue = True
            while is_continue:
                filer_file = cy_docs.EXPR(qr.fields.SizeInBytes == qr.fields.SizeUploaded)
                process_time = datetime.datetime.utcnow()
                process_field= f"{process_time.year}_{process_time.month: 02}_{process_time.day :02}_{process_time.minute: 02}"

                # fileter_reindex = cy_docs.not_exists(getattr(cy_docs.fields.ReIndexInfo,process_field))
                fileter_reindex = (
                        (qr.fields.HasThumb == False) |
                        (cy_docs.not_exists(qr.fields.HasThumb))
                )
                fileter_thumb_able = (
                        (qr.fields.ThumbnailsAble == False) |
                        (cy_docs.not_exists(qr.fields.ThumbnailsAble))
                )
                filter = (fileter_reindex | fileter_thumb_able) & (qr.fields.ThumbFileId == None) & (qr.fields.Status==1)
                try:
                    items = qr.context.aggregate().match(
                        filter
                    ).sort(
                        qr.fields.RegisterOn.desc()
                    ).limit(100)
                    items_list = list(items)
                    is_continue = len(items_list)>0
                    for x in items:
                        ext: str = x[qr.fields.FileExt]
                        if ext is None:
                            ext = pathlib.Path(x[qr.fields.FileName]).suffix
                            if ext:
                                ext=ext[1:]
                        if ext is None:
                            continue
                        mime_type:str = x[qr.fields.MimeType]
                        if mime_type is None:
                            qr.context.update(
                                qr.fields.id == x.id,
                                qr.fields.ThumbnailsAble<<False
                            )
                        if ext is None:
                            qr.context.update(
                                qr.fields.id == x.id,
                                qr.fields.ThumbnailsAble << False
                            )
                        is_ok = ext.lower() in config.ext_office_file
                        is_ok = is_ok or (mime_type.startswith("image/"))
                        is_ok = is_ok or (mime_type.startswith("video/"))
                        if not  is_ok:
                            continue
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
                                qr.fields.ThumbnailsAble << True
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
