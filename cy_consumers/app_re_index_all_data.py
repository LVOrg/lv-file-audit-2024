import datetime
import os.path
import pathlib
import time

import bson

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
            msg_broker.delete(msg_info)
            txt_msg = f"{MSG_APP_RE_INDEX_ALL} receive message from app {msg_info.AppName} at time {msg_info.CreatedOn}"
            self.logger.info(txt_msg)
            qr = self.files_service.get_queryable_doc(msg_info.AppName)
            fileter = (
                    (qr.fields.HasThumb == False) |
                    (cy_docs.not_exists(qr.fields.HasThumb))|
                    (cy_docs.not_exists(qr.fields.ThumbFileId))|
                    (qr.fields.ThumbFileId==None)
            )

            qr.context.update(
                fileter,
                qr.fields.ReIndex<<False
            )
            agg = qr.context.aggregate().match(
                (qr.fields.ReIndex==False) & fileter
            ).sort(
                qr.fields.RegisterOn.desc()
            ).limit(1000)
            items = list(agg)

            while len(items):
                for x in items:
                    if x.MainFileId and isinstance(x.MainFileId,str) and "local://" not in x.MainFileId:
                        qr.context.update(
                            qr.fields.id==x.id,
                            qr.fields.HasThumb<<True
                        )
                        continue
                    if x.MainFileId and isinstance(x.MainFileId,bson.ObjectId):
                        qr.context.update(
                            qr.fields.id==x.id,
                            qr.fields.HasThumb<<True
                        )
                        continue
                    if x.ThumbFileId  and isinstance(x.ThumbFileId,str) and x.ThumbFileId.startswith("local://"):
                        thumb_path = os.path.join( config.file_storage_path,x.ThumbFileId.split("://")[1])
                        if os.path.isfile(thumb_path):
                            qr.context.update(
                                qr.fields.id == x.id,
                                qr.fields.HasThumb << True
                            )
                            continue
                    ext: str = x[qr.fields.FileExt]
                    if ext is None:
                        ext = pathlib.Path(x[qr.fields.FileName]).suffix
                        if ext:
                            ext = ext[1:]
                    if ext is None:
                        continue
                    mime_type: str = x[qr.fields.MimeType]
                    if mime_type is None:
                        qr.context.update(
                            qr.fields.id == x.id,
                            qr.fields.ThumbnailsAble << False
                        )
                    if ext is None:
                        qr.context.update(
                            qr.fields.id == x.id,
                            qr.fields.ThumbnailsAble << False
                        )
                    is_ok = ext.lower() in config.ext_office_file
                    is_ok = is_ok or (mime_type.startswith("image/"))
                    is_ok = is_ok or (mime_type.startswith("video/"))
                    if not is_ok:
                        continue
                    txt_msg = f"{msg_info.AppName}\t{x[qr.fields.FileName]} re-index content with {MSG_FILE_UPLOAD}"
                    try:

                        self.logger.info(txt_msg)
                        print(x.FullFileNameLower)
                        msg_broker.emit(
                            app_name=msg_info.AppName,
                            message_type=MSG_FILE_UPLOAD,
                            data=x
                        )
                        qr.context.update(
                            qr.fields.id == x.id,
                            qr.fields.ThumbnailsAble << True,
                            qr.fields.ReIndex<<True
                        )

                    except Exception as e:
                        self.logger.error(e)
                time.sleep(30)
                items = list(agg)

            print("Run")
        except Exception as e:
            self.logger.error(e)
            msg_broker.delete(msg_info)
