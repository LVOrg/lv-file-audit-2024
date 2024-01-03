"""
Message work flow:

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
import time
import typing
import uuid

MSG_FILE_UPLOAD = "files.upload"
"""
Whenever file was uploaded, the message would be raised
  
"""
MSG_FILE_GENERATE_IMAGE_FROM_VIDEO = "files.upload.generate.image.from.video"
"""
Get one frame in video file then create new image from that frame \n
Nhận một khung hình trong tệp video, sau đó tạo hình ảnh mới từ khung hình đó

"""
MSG_FILE_EXTRACT_TEXT_FROM_VIDEO = "files.extract.text.from.video"
"""
Detect frame in video file if that frame contains readable text.
Use readable text for Content Search \n
Phát hiện khung trong tệp video nếu khung đó chứa văn bản có thể đọc được.
Sử dụng văn bản có thể đọc được cho Tìm kiếm Nội dung
"""
MSG_FILE_GENERATE_IMAGE_FROM_OFFICE = "files.upload.generate.image.from.office"
"""
    Tell Consumer generate an image file from Office file or Office file readable or Office file compatibility format \n
    tạo tệp hình ảnh từ tệp Office hoặc tệp Office có thể đọc được hoặc định dạng tương thích với tệp Office
"""
MSG_FILE_GENERATE_IMAGE_FROM_PDF = "files.upload.generate.image.from.pdf"
"""
Tell Consumer generate an image file from PDF file \n
Nói  Consumer tạo một file hình ảnh từ tệp PDF
"""
MSG_FILE_GENERATE_PDF_FROM_IMAGE = "files.upload.generate.pdf"
"""
File-Service will collect any readable-content from any material \n
Include image file. This message will tel a certain Consumer convert image file int PDF file with readable-content \n
Dịch vụ tệp sẽ thu thập mọi nội dung có thể đọc được từ mọi tài liệu \n
Bao gồm tập tin hình ảnh. Message sẽ gọi cho một Consumer nhất định chuyển đổi tệp hình ảnh thành tệp PDF có nội dung có thể đọc được
"""
MSG_FILE_GENERATE_THUMBS = "files.upload.generate.thumbs"
"""
Generate some thumbnail according to file  with thumbnail-size-infor in message's body \n
Tạo một số hình thu nhỏ theo tệp với thông tin kích thước hình thu nhỏ trong nội dung thư
"""
MSG_FILE_OCR_CONTENT = "files.upload.ocr.content"
"""
Tell Consumer make OCR file from PDF file \n
Nói Consumer tạo tệp OCR từ tệp PDF
"""
MSG_FILE_SAVE_DEFAULT_THUMB = "files.upload.save.default.thumb"
MSG_FILE_SAVE_CUSTOM_THUMB = "files.upload.save.custom.thumb"
MSG_FILE_SAVE_OCR_PDF = "files.upload.save.ocr.pdf"
MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE = "files.upload.update.search.from.file"
"""
Human-readable-content file could be used for Search Content Engine
The message will force another Comumser to do that \n
Tệp nội dung con người có thể đọc được có thể được sử dụng cho Search Content Engine
Tin nhắn sẽ buộc một Conumser khác làm điều đó
"""
MSG_FILE_EXTRACT_TEXT_FROM_IMAGE = "files.upload.extract.text.from.file"
MSG_FILE_MOVE_TENANT = "files.move.tenant"
MSG_FILE_PAGES_CONTENT = "files.pages.content"
"""
Parse page by page of file put to Elasticsearch and MongoDb
"""
MSG_FILE_DOC_LAYOUT_ANALYSIS = "files.document.layout.analysis"
"""deepdoctection is a Python library that orchestrates document extraction and document layout analysis tasks using 
deep learning models. It does not implement models but enables you to build pipelines using highly acknowledged 
libraries for object detection, OCR and selected NLP tasks and provides an integrated framework for fine-tuning, 
evaluating and running models. For more specific text processing tasks use one of the many other great NLP libraries"""
MSG_FILE_EXTRACT_AUDIO_FROM_VIDEO = "files.upload.extract.audio.from.video"
MSG_APP_RE_INDEX_ALL = "apps.re-index.all"
MSG_LIBRE_OFFICE_CONVERT_TO_IMAGE = "libre.office.convert.process"
MSG_LIBRE_OFFICE_CONVERT_TO_IMAGE_FINISH = "libre.office.convert.finish"
MSG_EXTRACT_TEXT_FROM_OFFICE_FILE = ""
import datetime
from typing import List
from cyx.common import config

ext_office_file = config.ext_office_file
ext_video_file = config.ext_video_file
ext_image_file = config.ext_image_file
MSG_MATRIX = {}
from enum import Enum

PROCESSING_FILE = "PROCESSING_FILE"
class MsgEnum(Enum):
    EXTRACT_TEXT_FROM_VIDEO = "EXTRACT_TEXT_FROM_VIDEO"
    GEN_IMAGE_FROM_VIDEO = "GEN_IMAGE_FROM_VIDEO"
    GEN_IMAGE_FROM_OFFICE = "GEN_IMAGE_FROM_OFFICE"
    EXTRACT_TEXT_FROM_IMAGE = "EXTRACT_TEXT_FROM_IMAGE"
    UPDATE_TEXT_TO_SEARCH_ENGINE = "UPDATE_TEXT_TO_SEARCH_ENGINE"
    EXTRACT_TEXT_FROM_OFFICE = "EXTRACT_TEXT_FROM_OFFICE"
    UPDATE_CUSTOM_THUMB = "UPDATE_CUSTOM_THUMB"
    UPDATE_DEFAULT_THUMB = "UPDATE_DEFAULT_THUMB"
    GEN_THUMB = "GEN_THUMB"
    UPLOAD = "UPLOAD"


__MSG_MATRIX_IMAGE_FILE__ = {
    MsgEnum.GEN_THUMB.name: {
        MsgEnum.UPDATE_DEFAULT_THUMB.name: {},
        MsgEnum.UPDATE_CUSTOM_THUMB.name: {}
    },
    MsgEnum.EXTRACT_TEXT_FROM_IMAGE.name: {
        MsgEnum.UPDATE_TEXT_TO_SEARCH_ENGINE.name: {}
    }
}
__MSG_MATRIX_OFFICE_FILE__ = {
    MsgEnum.EXTRACT_TEXT_FROM_OFFICE.name: {
        MsgEnum.UPDATE_TEXT_TO_SEARCH_ENGINE.name: {}
    },
    MsgEnum.GEN_IMAGE_FROM_OFFICE.name: {
        MsgEnum.GEN_THUMB.name: {
            MsgEnum.UPDATE_DEFAULT_THUMB.name: {},
            MsgEnum.UPDATE_CUSTOM_THUMB.name: {}
        }
    }
}
__MSG_MATRIX_VIDEO_FILE__ = {
    MsgEnum.GEN_IMAGE_FROM_VIDEO.name: {
        MsgEnum.UPDATE_DEFAULT_THUMB.name: {},
        MsgEnum.UPDATE_CUSTOM_THUMB.name: {}
    },
    MsgEnum.EXTRACT_TEXT_FROM_VIDEO.name: {
        MsgEnum.UPDATE_TEXT_TO_SEARCH_ENGINE.name: {}
    }
}
import copy

for x in ext_image_file:
    MSG_MATRIX[x] = copy.deepcopy(__MSG_MATRIX_IMAGE_FILE__)
for x in ext_office_file:
    MSG_MATRIX[x] = copy.deepcopy(__MSG_MATRIX_OFFICE_FILE__)
for x in ext_video_file:
    MSG_MATRIX[x] = copy.deepcopy(__MSG_MATRIX_VIDEO_FILE__)
class MessageInfo:
    def __init__(self):
        self.MsgType: str = None
        self.Data: dict = None
        self.CreatedOn: datetime.datetime = None
        self.AppName: str = None
        self.Id: str = None
        self.tags = None
        self.deleted = False


class MessageService:
    def emit(cls, app_name: str, message_type: str, data: dict):
        pass

    def re_emit(cls, msg: MessageInfo):
        pass

    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:
        pass

    def get_type(self) -> str:
        return "unknown"

    def consume(self, handler, msg_type: str):
        """
        Start Consumer
        :param handler:
        :param msg_type:
        :return:
        """
        pass

    def delete(self, item: MessageInfo):
        pass

    def reset_status(self, message_type: str):
        """
        Reset status
        :param message_type:
        :return:
        """
        raise NotImplemented

    def lock(self, item: MessageInfo):
        pass

    def unlock(self, item: MessageInfo):
        pass

    def is_lock(self, item: MessageInfo):
        pass

    def consume(self, handler, msg_type: str):
        pass

    def close(self):
        pass


def broker(message: str):
    from cy_docs import define, get_doc
    import cyx.common.base
    import cy_kit
    db_connect = cy_kit.singleton(cyx.common.base.DbConnect)

    @define(name="SYS_DelayMessage",
            indexes=["AppName", "UploadID", "MessageType"],
            uniques=["AppName,UploadID,MessageType"]
            )
    class SYS_DelayMessage:
        AppName: typing.Optional[str]
        UploadId: typing.Optional[str]
        MessageType: typing.Optional[str]
        CreatedOn: typing.Optional[datetime.datetime]
        ModifiedOn: typing.Optional[datetime.datetime]
        ResumeCount: typing.Optional[int]
        MessageBody: typing.Optional[dict]

    sys_delay_message_docs = db_connect.db("admin").doc(SYS_DelayMessage)

    def __wrapper__(cls):
        from cyx.common.rabitmq_message import RabitmqMsg
        if not hasattr(cls, "on_receive_msg"):
            raise Exception(f"{cls.__module__}.{cls.__name__} must have function on_receive_msg")
        fx = getattr(cls, "on_receive_msg")
        if not callable(fx):
            raise Exception(f"on_receive_msg in {cls.__module__}.{cls.__name__} must be a function")
        if len(fx.__annotations__.keys()) < 2:
            raise Exception(f"on_receive_msg in {cls.__module__}.{cls.__name__} must be a 2 args")
        if fx.__annotations__.get("msg_info") is None:
            raise Exception(f"The first arg of on_receive_msg in {cls.__module__}.{cls.__name__} must name 'msg_info'")
        if fx.__annotations__.get("msg_broker") is None:
            raise Exception(
                f"The second arg of on_receive_msg in {cls.__module__}.{cls.__name__} must name 'msg_broker'")
        if fx.__annotations__["msg_info"] != MessageInfo:
            raise Exception(
                f"msg_info arg of on_receive_msg in {cls.__module__}.{cls.__name__} must be {MessageInfo.__module__} {MessageInfo.__name__}")
        if fx.__annotations__["msg_broker"] != MessageService:
            raise Exception(
                f"msg_broker arg of on_receive_msg in {cls.__module__}.{cls.__name__} must be {MessageService.__module__} {MessageService.__name__}")

        def __set_msg__(owner, str_msg: str):
            owner.message_type = message
            return owner

        setattr(cls, "__set_msg__", __set_msg__)
        import cy_kit
        import pika
        ins = cy_kit.singleton(cls)
        ins.__set_msg__(message)
        setattr(ins, "__msg_process_fail_count__", 0)
        msg = cy_kit.singleton(RabitmqMsg)
        from cyx.loggers import LoggerService
        logger = cy_kit.singleton(LoggerService)
        setattr(ins, "__msg_broker__", msg)

        def on_receive_msg(msg_info: MessageInfo):
            ins.on_receive_msg(msg_info, msg)
            ins.__msg_process_fail_count__ = 4
            is_ok = True

        def on_receive_msg_(msg_info: MessageInfo):
            ins.__msg_process_fail_count__ = 0
            is_ok = False
            while ins.__msg_process_fail_count__ < 3:
                try:
                    ins.on_receive_msg(msg_info, msg)
                    ins.__msg_process_fail_count__ = 4
                    is_ok = True
                except pika.exceptions.ChannelClosedByBroker as e:
                    ins.__msg_process_fail_count__ += 1
                    print(f"{ins.message_type} fail. Re try {ins.__msg_process_fail_count__}")
                    time.sleep(0.5)
                    logger.error(e, msg_info=dict(
                        msg=f"Fail process {ins.message_type}",
                        msg_body=msg_info.Data,
                        app_name=msg_info.AppName
                    ))

                except Exception as e:
                    ins.__msg_process_fail_count__ += 1
                    print(f"{ins.message_type} fail. Re try {ins.__msg_process_fail_count__}")
                    time.sleep(0.5)
                    logger.error(e, msg_info=dict(
                        msg=f"Fail process {ins.message_type}",
                        msg_body=msg_info.Data,
                        app_name=msg_info.AppName
                    ))
            if not is_ok:
                filter = ((sys_delay_message_docs.fields.UploadId == msg_info.Data["UploadId"]) &
                          (sys_delay_message_docs.fields.AppName == msg_info.AppName) &
                          (sys_delay_message_docs.fields.MessageType == ins.message_type))
                data_item = sys_delay_message_docs.context.find_one(filter)
                if data_item:
                    data_item[sys_delay_message_docs.fields.ResumeCount] += 1
                    data_item[sys_delay_message_docs.fields.ModifiedOn] = datetime.datetime.utcnow()
                    sys_delay_message_docs.context.update(
                        sys_delay_message_docs.fields.Id == data_item["_id"],
                        sys_delay_message_docs.fields.ModifiedOn << datetime.datetime.utcnow(),
                        sys_delay_message_docs.fields.ResumeCount << data_item[
                            sys_delay_message_docs.fields.ResumeCount]
                    )
                else:
                    sys_delay_message_docs.context.insert_one(
                        sys_delay_message_docs.fields.Id << str(uuid.uuid4()),
                        sys_delay_message_docs.fields.ResumeCount << 0,
                        sys_delay_message_docs.fields.MessageType << ins.message_type,
                        sys_delay_message_docs.fields.AppName << msg_info.AppName,
                        sys_delay_message_docs.fields.UploadId << msg_info.Data["UploadID"],
                        sys_delay_message_docs.fields.MessageBody << msg_info.Data
                    )
            # if msg_info.tags and hasattr(msg_info.tags.get('ch',{}),"basic_ack"):
            #     msg_info.tags['ch'].basic_ack()

            msg.delete(msg_info)

        msg.consume(
            msg_type=ins.message_type,
            handler=on_receive_msg
        )
        return ins

    return __wrapper__
