# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_thumbs.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
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
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

import json

temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)
image_extractor_service = cy_kit.singleton(ImageExtractorService)
msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService
from cy_xdoc.services.files import FileServices
import PIL
from cyx.loggers import  LoggerService
__check_id__ ={}
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_THUMBS)
class Process:
    def __init__(self,
                 file_services = cy_kit.singleton(FileServices),
                 logger = cy_kit.singleton(LoggerService)
                 ):
        self.file_services = file_services
        self.logger = logger

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        processing_file = msg_info.Data.get("processing_file")
        upload_id = msg_info.Data.get("_id") or msg_info.Data.get("UploadId")
        if not upload_id:
            msg.delete(msg_info)
            return
        upload_item = self.file_services.get_upload_register(
            app_name=  msg_info.AppName,
            upload_id = upload_id
        )
        if not upload_item:
            msg.delete(msg_info)
            return
        if upload_item.MsgCheckList is None:
            upload_item.MsgCheckList = {}
        check = self.file_services.get_msg_check_list(
            app_name=msg_info.AppName,
            upload_id=upload_id,
            key = cyx.common.msg.MSG_FILE_GENERATE_THUMBS
        )
        if check !=0:
            print(f"delete {upload_id}/{msg_info.tags['method'].delivery_tag}")
            msg.delete(msg_info)
            return
        else:
            self.file_services.update_msg_check_list(
                app_name=msg_info.AppName,
                upload_id=upload_id,
                key=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                value=1
            )





        if  processing_file is None:
            processing_file = msg_info.Data.get(cyx.common.msg.PROCESSING_FILE)
        if processing_file is None:
            full_file_path = None
            file_ext = msg_info.Data.get("FileExt")
            local_file = msg_info.Data.get("StoragePath")
            if isinstance(local_file, str) and "://" in local_file:
                local_file = os.path.join(config.file_storage_path, local_file.split("://")[1])
                if os.path.isfile(local_file):
                    processing_file = local_file

            if file_ext is None:
                file_ext = pathlib.Path(msg_info.Data.get("FileName")).suffix
                if file_ext:
                    file_ext = file_ext[1:]
            if file_ext is None:
                msg.delete(msg_info)
                return

            if not processing_file:
                try:
                    processing_file = temp_file.get_path(
                        app_name=msg_info.AppName,
                        file_ext=file_ext,
                        upload_id=upload_id,
                        file_id=msg_info.Data.get("MainFileId")
                    )
                except FileNotFoundError:
                    msg.delete(msg_info)
                    """
                    Eliminate message never occur again
                    Loại bỏ tin nhắn không bao giờ xảy ra nữa
                    """
                    self.logger.info(f"msg={self.message_type}, upload_file={full_file_path},file was not found")
                    return
        if not processing_file:
            file_ext = msg_info.Data.get("FileExt")
            if file_ext is None:
                file_ext = pathlib.Path(msg_info.Data["FileName"]).suffix
            if file_ext:
                file_ext=file_ext[1:]
            full_file = msg_info.Data.get("processing_file", temp_file.get_path(
                app_name=msg_info.AppName,
                upload_id=msg_info.Data.get("_id","UploadID"),
                file_ext=file_ext,
                file_id=msg_info.Data.get("MainFileId")

            ))
            if os.path.isfile(full_file):
                processing_file = full_file
        if processing_file is None:
            msg.delete(msg_info)
            return

        key_check = f'{upload_id}/{msg_info.tags["method"].delivery_tag}'


        if not os.path.isfile(processing_file):
            msg.delete(msg_info)
            __check_id__[key_check]=upload_id
            return
        self.logger.info(processing_file)
        default_thumb = None
        try:
            default_thumb = image_extractor_service.create_thumb(
                image_file_path=processing_file,
                size=700,
                id = upload_id

            )

            # default_thumb_path = temp_file.move_file(
            #     from_file=default_thumb,
            #     app_name=msg_info.AppName,
            #     sub_dir=f"default_thumb/{upload_id}"
            # )
            msg_info.Data["processing_file"] = default_thumb
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                data=msg_info.Data
            )

            if msg_info.Data.get("AvailableThumbSize"):
                available_thumbs = []
                sizes = [int(x) for x in msg_info.Data.get("AvailableThumbSize").split(',') if x.isnumeric()]
                for x in sizes:
                    custome_thumb = image_extractor_service.create_thumb(
                        image_file_path=processing_file,
                        size=x,
                        id=upload_id

                    )
                    # custome_thumb_path = temp_file.move_file(
                    #     from_file=custome_thumb,
                    #     app_name=msg_info.AppName,
                    #     sub_dir=f"thumb_{x}/{msg_info.Data['_id']}"
                    # )
                    msg_info.Data["processing_file"] = custome_thumb
                    msg.delete(msg_info)
                    msg.emit(
                        app_name=msg_info.AppName,
                        message_type=cyx.common.msg.MSG_FILE_SAVE_CUSTOM_THUMB,
                        data=msg_info.Data
                    )
                    self.logger.info(f"{cyx.common.msg.MSG_FILE_SAVE_CUSTOM_THUMB}->{msg_info.Data['processing_file']}")
                    available_thumbs += [f"thumbs/{msg_info.Data['_id']}/{x}.webp"]
                self.file_services.update_available_thumbs(
                    upload_id=upload_id,
                    app_name=msg_info.AppName,
                    available_thumbs=available_thumbs

                )
            self.file_services.update_msg_check_list(
                app_name=msg_info.AppName,
                upload_id = upload_id,
                key= cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                value=1
            )
            self.file_services.update_msg_check_list(
                app_name=msg_info.AppName,
                upload_id=upload_id,
                key=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                value=2
            )
        except FileNotFoundError:
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                data=self.file_services.get_upload_register(
                    app_name=msg_info.AppName,
                    upload_id=upload_id
                )

            )
            msg.delete(msg_info)
