# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_thumbs.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import shutil
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

from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

import json

temp_file = cy_kit.singleton(TempFiles)
pdf_file_service = cy_kit.singleton(PDFService)
from cyx.common.rabitmq_message import RabitmqMsg
msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService

import PIL
from cyx.loggers import  LoggerService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
__check_id__ ={}
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_THUMBS)
class Process:
    def __init__(self,
                 file_services = cy_kit.singleton(FileServices),
                 content_service=cy_kit.singleton(ContentService),
                 image_extractor_service=cy_kit.singleton(ImageExtractorService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 logger = cy_kit.singleton(LoggerService)
                 ):
        self.file_services = file_services
        self.content_service=content_service
        self.image_extractor_service= image_extractor_service
        self.logger = logger
        self.mongodb_service= mongodb_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        print(msg_info)
        master_resource = self.content_service.get_master_resource(msg_info)
        print(master_resource)
        doc_context= self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)

        resource = self.content_service.get_resource(msg_info)
        print(resource)
        delivery_tag= msg_info.tags["method"].delivery_tag
        parent_msg = msg_info.parent_msg
        unique_dir = pathlib.Path(resource).parent.name
        try:
            import mimetypes
            mt,_ = mimetypes.guess_type(resource)
            if not mt.startswith("image/"):
                _doc_context = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
                _upload_item = _doc_context.context.find_one(
                    doc_context.fields.id == unique_dir
                )
                if _upload_item is None:
                    msg.delete(msg_info)
                    return
                master_resource = self.content_service.get_master_resource(msg_info)
                if not master_resource:
                    msg.delete(msg_info)
                    return

                if not os.path.isfile(master_resource):
                    msg.delete(msg_info)
                    return
                msg.emit(
                    app_name=msg_info.AppName,
                    message_type=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                    data=msg_info.Data,
                    parent_msg=parent_msg,
                    parent_tag=delivery_tag,
                    resource=master_resource

                )

                msg.delete(msg_info)
                return
            default_thumbs = self.image_extractor_service.create_thumb(
                image_file_path=resource,
                size=700,
                id=unique_dir

            )
            try:
                shutil.move(default_thumbs,os.path.join(pathlib.Path(master_resource).parent.__str__(),os.path.split(default_thumbs)[1]))
            except:
                pass

            doc_context = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
            upload_item = doc_context.context.find_one(
                doc_context.fields.id== unique_dir
            )
            if upload_item is None:
                msg.delete(msg_info)
                return
            thumbs = upload_item[doc_context.fields.AvailableThumbSize]
            if isinstance(thumbs,str):
                sizes = [int(x) for  x in thumbs.split(',') if x.lstrip(" ").rstrip(" ").isnumeric()]
                for x in sizes:
                    default_thumbs = self.image_extractor_service.create_thumb(
                        image_file_path=resource,
                        size=x,
                        id=unique_dir

                    )
                    try:
                        shutil.move(default_thumbs, os.path.join(pathlib.Path(master_resource).parent.__str__(),
                                                                 os.path.split(default_thumbs)[1]))
                    except:
                        pass
            doc_context.context.update(
                doc_context.fields.id == unique_dir,
                doc_context.fields.ThumbnailsAble<<True,
                doc_context.fields.HasThumb<<True
            )
            msg.delete(msg_info)
        except FileNotFoundError as e:
            master_resource= self.content_service.get_master_resource(msg_info)
            if master_resource is None:
                msg.delete(msg_info)
            if not os.path.isfile(master_resource):
                msg.delete(msg_info)
            else:
                msg.emit(
                    app_name=msg_info.AppName,
                    message_type= cyx.common.msg.MSG_FILE_UPLOAD,
                    data=msg_info.Data,
                    resource=master_resource
                )
                msg.delete(msg_info)


    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
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

        self.logger.info(processing_file)
        default_thumb = None
        try:
            default_thumb = self.image_extractor_service.create_thumb(
                image_file_path=processing_file,
                size=700,
                id=upload_id

            )
        except PIL.UnidentifiedImageError as e:
            msg.delete(msg_info)
            return
        msg_info.Data["processing_file"] = default_thumb
        main_file_id = msg_info.Data.get("MainFileId")

        if isinstance(main_file_id,str) and main_file_id.startswith("local://"):
            rel_path = main_file_id.split("://")[1]
            real_thumb_path = pathlib.Path(os.path.join(config.file_storage_path,rel_path)).parent.__str__()
            shutil.move(default_thumb,os.path.join(real_thumb_path,os.path.split(rel_path)[1]+".webp"))
        else:
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_SAVE_DEFAULT_THUMB,
                data=msg_info.Data
            )

        if msg_info.Data.get("AvailableThumbSize"):
            available_thumbs = []
            sizes = [int(x) for x in msg_info.Data.get("AvailableThumbSize").split(',') if x.isnumeric()]
            for x in sizes:
                custome_thumb = self.image_extractor_service.create_thumb(
                    image_file_path=processing_file,
                    size=x,
                    id=upload_id

                )
                if isinstance(main_file_id, str) and main_file_id.startswith("local://"):
                    rel_path = main_file_id.split("://")[1]
                    real_thumb_path = pathlib.Path(os.path.join(config.file_storage_path, rel_path)).parent.__str__()
                    shutil.move(custome_thumb, os.path.join(real_thumb_path, f"{x}.webp"))
                else:
                    msg_info.Data["processing_file"] = custome_thumb

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

        msg.delete(msg_info)
