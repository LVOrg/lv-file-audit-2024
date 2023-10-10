import typing

from pydantic import BaseModel
import datetime


class FileUploadRegisterInfo(BaseModel):
    UploadId: typing.Optional[str]
    FileName: typing.Optional[str]
    Status: typing.Optional[int]
    SizeInHumanReadable: typing.Optional[str]
    ServerFileName: typing.Optional[str]
    IsPublic: typing.Optional[bool]
    FullFileName: typing.Optional[str]
    MimeType: typing.Optional[str]
    FileSize: typing.Optional[int]
    UploadId: typing.Optional[str]
    CreatedOn: typing.Optional[datetime.datetime]
    FileNameOnly: typing.Optional[str]
    UrlOfServerPath: typing.Optional[str]
    """
    Abs url for content accessing
    http://172.16.1.210:8011/api/lv-test/file/22bd557d-e78f-4157-a735-2d95fc64d302/story_content/story.js
    """
    AppName: typing.Optional[str]
    RelUrlOfServerPath: typing.Optional[str]
    """
    Relative url for content processing
    The fucking looks like this /lv-test/file/22bd557d-e78f-4157-a735-2d95fc64d302/story_content/story.js
    """
    ThumbUrl: typing.Optional[str]
    """
    The fucking main thumb look like
    http://172.16.1.210:8011/api/lv-test/thumb/0048135e-50e5-4f56-8c89-b2f8fe83b06b/story.js.webp
    """
    AvailableThumbs: typing.Optional[typing.List[str]]
    Media: typing.Optional[dict]
    HasThumb: typing.Optional[bool]
    OcrContentUrl: typing.Optional[str]
    OCRFileId: typing.Optional[str]
    SearchEngineErrorLog: typing.Optional[str]
    SearchEngineMetaIsUpdate: typing.Optional[bool]
    BrokerMsgUploadIsOk: typing.Optional[bool]
    BrokerErrorLog: typing.Optional[str]


class DataMoveTanent(BaseModel):
    FromAppName: str
    ToAppName: str
    UploadIds: typing.List[str]
class DataMoveTanentParam(BaseModel):
    Data: DataMoveTanent