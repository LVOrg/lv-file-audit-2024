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
import datetime
from typing import List


class MessageInfo:
    def __init__(self):
        self.MsgType: str = None
        self.Data: dict = None
        self.CreatedOn: datetime.datetime = None
        self.AppName: str = None
        self.Id: str = None
        self.tags = None


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
    def __wrapper__(cls):
        from cyx.common.rabitmq_message import RabitmqMsg
        if not hasattr(cls, "on_receive_msg"):
            raise Exception(f"{cls.__module__}.{cls.__name__} must have function on_receive_msg")
        fx = getattr(cls, "on_receive_msg")
        if not callable(fx):
            raise Exception(f"on_receive_msg in {cls.__module__}.{cls.__name__} must be a function")
        if len(fx.__annotations__.keys())<2:
            raise Exception(f"on_receive_msg in {cls.__module__}.{cls.__name__} must be a 2 args")
        if fx.__annotations__.get("msg_info") is None:
            raise Exception(f"The first arg of on_receive_msg in {cls.__module__}.{cls.__name__} must name 'msg_info'")
        if fx.__annotations__.get("msg_broker") is None:
            raise Exception(f"The second arg of on_receive_msg in {cls.__module__}.{cls.__name__} must name 'msg_broker'")
        if fx.__annotations__["msg_info"] != MessageInfo:
            raise Exception(f"msg_info arg of on_receive_msg in {cls.__module__}.{cls.__name__} must be {MessageInfo.__module__} {MessageInfo.__name__}")
        if fx.__annotations__["msg_broker"] != MessageService:
            raise Exception(f"msg_broker arg of on_receive_msg in {cls.__module__}.{cls.__name__} must be {MessageService.__module__} {MessageService.__name__}")
        def __set_msg__(owner, str_msg: str):
            owner.message_type = message
            return owner

        setattr(cls, "__set_msg__", __set_msg__)
        import cy_kit
        ins = cy_kit.singleton(cls)
        ins.__set_msg__(message)
        msg = cy_kit.singleton(RabitmqMsg)
        def on_receive_msg(msg_info: MessageInfo):
            ins.on_receive_msg(msg_info,msg)
        msg.consume(
            msg_type=ins.message_type,
            handler=on_receive_msg
        )
        return ins

    return __wrapper__
