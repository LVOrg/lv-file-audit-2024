"""
This consumer will receive message 'files.upload' from broker. Then generate some messages and pervasive them to
other consumer
---------------------------------------------------------
Consumer này sẽ nhận được tin nhắn 'files.upload' từ broker. Sau đó, tạo một số thông điệp và phổ biến chúng đến Consumer khác
--------------------------------------------

MSG_FILE_UPLOAD
├── MSG_FILE_GENERATE_IMAGE_FROM_VIDEO (*here*)
│   ├── MSG_FILE_GENERATE_PDF_FROM_IMAGE
│   │   └── MSG_FILE_OCR_CONTENT
│   │       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
│   └── MSG_FILE_GENERATE_THUMBS
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB
│       └── MSG_FILE_SAVE_CUSTOM_THUMB
├── MSG_FILE_EXTRACT_TEXT_FROM_VIDEO
├── MSG_FILE_GENERATE_IMAGE_FROM_OFFICE
│   └── MSG_FILE_GENERATE_THUMBS
│       ├── MSG_FILE_SAVE_DEFAULT_THUMB
│       └── MSG_FILE_SAVE_CUSTOM_THUMB
├── MSG_FILE_GENERATE_IMAGE_FROM_PDF
│   └── MSG_FILE_OCR_CONTENT
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
├── MSG_FILE_GENERATE_PDF_FROM_IMAGE
│   └── MSG_FILE_OCR_CONTENT
│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
├── MSG_FILE_GENERATE_THUMBS
│   ├── MSG_FILE_SAVE_DEFAULT_THUMB
│   └── MSG_FILE_SAVE_CUSTOM_THUMB
└── MSG_FILE_OCR_CONTENT
    └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE

"""

# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_upload.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService


msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)


def get_scree():
    messge_to_screen = f"\n" \
                       f"MSG_FILE_UPLOAD\n" \
                       f"├── MSG_FILE_GENERATE_IMAGE_FROM_VIDEO\n" \
                       f"│   ├── MSG_FILE_GENERATE_PDF_FROM_IMAGE\n" \
                       f"│   │   └── MSG_FILE_OCR_CONTENT\n" \
                       f"│   │       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE\n" \
                       f"│   └── MSG_FILE_GENERATE_THUMBS\n" \
                       f"│       ├── MSG_FILE_SAVE_DEFAULT_THUMB\n" \
                       f"│       └── MSG_FILE_SAVE_CUSTOM_THUMB\n" \
                       f"├── MSG_FILE_EXTRACT_TEXT_FROM_VIDEO\n" \
                       f"├── MSG_FILE_GENERATE_IMAGE_FROM_OFFICE\n" \
                       f"│   └── MSG_FILE_GENERATE_THUMBS\n" \
                       f"│       ├── MSG_FILE_SAVE_DEFAULT_THUMB\n" \
                       f"│       └── MSG_FILE_SAVE_CUSTOM_THUMB\n" \
                       f"├── MSG_FILE_GENERATE_IMAGE_FROM_PDF\n" \
                       f"│   └── MSG_FILE_OCR_CONTENT\n" \
                       f"│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE\n" \
                       f"├── MSG_FILE_GENERATE_PDF_FROM_IMAGE\n" \
                       f"│   └── MSG_FILE_OCR_CONTENT\n" \
                       f"│       └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE\n" \
                       f"├── MSG_FILE_GENERATE_THUMBS\n" \
                       f"│   ├── MSG_FILE_SAVE_DEFAULT_THUMB\n" \
                       f"│   └── MSG_FILE_SAVE_CUSTOM_THUMB\n" \
                       f"└── MSG_FILE_OCR_CONTENT\n" \
                       f"    └── MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE"
    return messge_to_screen


print(get_scree())

from cyx.loggers import LoggerService
from cyx.content_services import ContentService,ContentTypeEnum

@broker(message=cyx.common.msg.MSG_FILE_UPLOAD)
class Process:
    def __init__(self,
                 shared_storage_service=cy_kit.singleton(ShareStorageService),
                 content_service= cy_kit.singleton(ContentService),
                 logger=cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger
        self.content_service = content_service
        self.logger.info(f"consumer {cyx.common.msg.MSG_FILE_UPLOAD} init")
        self.temp_file = temp_file

        self.output_dir = shared_storage_service.get_temp_dir(self.__class__)

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        print(f'{msg_info.Data.get("MainFileId")}')
        content_type = self.content_service.get_type(msg_data= msg_info.Data)
        upload_id = msg_info.Data.get("_id") or msg_info.Data.get("UploadId")
        resource = self.content_service.get_resource(msg_info=msg_info)
        if content_type== ContentTypeEnum.Office:
            msg.emit(
                app_name=msg_info.AppName,
                message_type= cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
                parent_msg= msg_info.MsgType,
                parent_tag= msg_info.tags['method'].delivery_tag,
                require_tracking= True,
                data=msg_info.Data

            )
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_OFFICE,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags['method'].delivery_tag,
                require_tracking=True,
                data=msg_info.Data

            )
            msg.delete(msg_info)
        if content_type== ContentTypeEnum.Image:
            msg.emit(
                app_name=msg_info.AppName,
                message_type= cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                parent_msg= msg_info.MsgType,
                parent_tag= msg_info.tags['method'].delivery_tag,
                require_tracking= True,
                data=msg_info.Data

            )
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_IMAGE,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags['method'].delivery_tag,
                require_tracking=True,
                data=msg_info.Data

            )
            msg.delete(msg_info)
        if content_type== ContentTypeEnum.Pdf:
            msg.emit(
                app_name=msg_info.AppName,
                message_type= cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF,
                parent_msg= msg_info.MsgType,
                parent_tag= msg_info.tags['method'].delivery_tag,
                require_tracking= True,
                data=msg_info.Data

            )
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_PDF,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags['method'].delivery_tag,
                require_tracking=True,
                data=msg_info.Data

            )
            msg.delete(msg_info)
        if content_type== ContentTypeEnum.Video:
            msg.emit(
                app_name=msg_info.AppName,
                message_type= cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO,
                parent_msg= msg_info.MsgType,
                parent_tag= msg_info.tags['method'].delivery_tag,
                require_tracking= True,
                data=msg_info.Data

            )
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_VIDEO,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags['method'].delivery_tag,
                require_tracking=True,
                data=msg_info.Data

            )
            msg.delete(msg_info)
        else:
            msg.delete(msg_info)
    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        full_file_path = None
        file_ext = msg_info.Data.get("FileExt")
        local_file = msg_info.Data.get("StoragePath")
        if isinstance(local_file,str) and "://" in local_file:
            local_file = os.path.join(config.file_storage_path,local_file.split("://")[1])
            if os.path.isfile(local_file):
                full_file_path = local_file

        if file_ext is None:
            file_ext = pathlib.Path(msg_info.Data.get("FileName")).suffix
            if file_ext:
                file_ext=file_ext[1:]
        if not full_file_path:
            try:
                full_file_path = temp_file.get_path(
                    app_name=msg_info.AppName,
                    file_ext=file_ext,
                    upload_id=msg_info.Data.get("_id") or msg_info.Data.get("UploadId") ,
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
        msg_info.Data["processing_file"] = full_file_path
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

        self.logger.info(f"Receive file {full_file_path}")
        if not isinstance(msg_info, MessageInfo):
            """
            Someone who try to interfere directly to  Broker System create invalid  message, skip in this case 
            Ai đó cố gắng can thiệp trực tiếp vào Hệ thống Broker tạo thông báo không hợp lệ, bỏ qua trong trường hợp này
            """
            raise Exception(f"msg param must be MessageInfo")

        import mimetypes
        mime_type, _ = mimetypes.guess_type(msg_info.Data['FullFileName'])
        msg_info.Data[cyx.common.msg.PROCESSING_FILE] = full_file_path
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_DOC_LAYOUT_ANALYSIS,
            data=msg_info.Data
        )
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_PAGES_CONTENT,
            data=msg_info.Data
        )
        print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")
        self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")
        if file_ext.lower() == "pdf":
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF,
                data=msg_info.Data
            )
            """
            Tell Consumer generate an image file from PDF file 
                Nói  Consumer tạo một file hình ảnh từ tệp PDF
            """
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF}\n{full_file_path}")
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT,
                data=msg_info.Data
            )
            """
            Tell Consumer make OCR file from PDF 
            Nói Consumer tạo tệp OCR từ tệp PDF
            """
            print(f"{cyx.common.msg.MSG_FILE_OCR_CONTENT}\n{full_file_path}")
        if file_ext.lower() in config.ext_office_file and file_ext.lower() != "pdf":
            """
            If file is Office file readable or Office file compatibility format
            Nếu tệp là tệp Office có thể đọc được hoặc định dạng tương thích với tệp Office
            """
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")
            self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")


            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE,
                data=msg_info.Data
            )
            """
            Human-readable-content file could be used for Search Content Engine
            """
            self.logger.info(f"{cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE}\n{full_file_path}")
            print(f"{cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE}\n{full_file_path}")
        if mime_type.startswith('video/'):
            """
            Video content
            """
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO,
                data=msg_info.Data
            )
            """
            Get one frame in video file then create new image from that frame 
            Nhận một khung hình trong tệp video, sau đó tạo hình ảnh mới từ khung hình đó
            """
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO}\n{full_file_path}")
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_VIDEO,
                data=msg_info.Data
            )
            """
            Detect frame in video file if that frame contains readable text.
            Use readable text for Content Search 
            Phát hiện khung trong tệp video nếu khung đó chứa văn bản có thể đọc được.
            Sử dụng văn bản có thể đọc được cho Tìm kiếm Nội dung
            """
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO}\n{full_file_path}")
        if mime_type.startswith('image/'):
            """
            """
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data
            )
            """
            Generate some thumbnail according to file  with thumbnail-size-infor in message's body
            Tạo một số hình thu nhỏ theo tệp với thông tin kích thước hình thu nhỏ trong nội dung thư
            """
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n{full_file_path}")
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_PDF_FROM_IMAGE,
                data=msg_info.Data
            )
            """
            File-Service will collect any readable-content from any material 
            Include image file. This message will tel a certain Consumer convert image file int PDF file with readable-content \n
                File-Service sẽ thu thập mọi nội dung có thể đọc được từ mọi tài liệu 
                Bao gồm tập tin hình ảnh. Message sẽ gọi cho một Consumer nhất định chuyển đổi tệp hình ảnh thành tệp PDF có nội dung có thể đọc được
            """
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE}\n{full_file_path}")

        msg.delete(msg_info)
        print(f"{full_file_path}\n is ok")
