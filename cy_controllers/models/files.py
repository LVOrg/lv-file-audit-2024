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

class FileContentSaveResult(BaseModel):
    Data: dict|None
    Error: dict|None

class PrivilegesType(BaseModel):
    Type: str|None
    Values: str|None
    """
    Separated by comma
    """
class FileContentSaveData(BaseModel):
    DocId: str|None
    MetaData: dict|None
    Privileges: typing.List[PrivilegesType]|None
    Content: str|None
class FileContentSaveArgs(BaseModel):
    data: FileContentSaveData
class ErrorInfo(BaseModel):
    Code: typing.Optional[str]
    Message: typing.Optional[str]


class DataPrivileges(BaseModel):
    UploadId: str
    Privileges: typing.List[PrivilegesType]


class Err(BaseModel):
    message: str


class AddPrivilegesResult(BaseModel):
    is_ok: bool
    error: typing.Optional[Err]

class CloneFileResult(BaseModel):
    Info: typing.Optional[dict]
    Error: typing.Optional[ErrorInfo]
class SkipFileProcessingOptionVirtual(BaseModel):
    All: bool|None = False
    pass
from  cyx.common.msg import (
    MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
    MSG_FILE_EXTRACT_TEXT_FROM_VIDEO,
    MSG_FILE_GENERATE_THUMBS,
    MSG_FILE_OCR_CONTENT,
    MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
)
list_of_attrs=[
    MSG_FILE_OCR_CONTENT,
    MSG_FILE_GENERATE_THUMBS,
    MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
    MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
]
from pydantic.fields import ModelField
SkipFileProcessingOptions = SkipFileProcessingOptionVirtual
skip_all_field = SkipFileProcessingOptionVirtual.__dict__["__fields__"]["All"]
for x in list_of_attrs:
    x_name = x.replace(".","_")
    x_field = ModelField(
        name=x_name,
        type_=bool,
        required=False,
        class_validators={},
        model_config=skip_all_field.model_config,
        default=False
    )
    SkipFileProcessingOptions.__dict__["__fields__"][x_name]=x_field

class DeleteFileResult(BaseModel):
    AffectedCount: typing.Optional[int]
    Error: typing.Optional[ErrorInfo]

class UploadInfoResult(BaseModel):
    UploadId: typing.Optional[str]
    FileName: typing.Optional[str]
    FileNameOnly: typing.Optional[str]
    FileExt: typing.Optional[str]
    HasThumb: typing.Optional[bool]
    SizeInBytes: typing.Optional[int]
    FullUrl: typing.Optional[str]
    RelUrl: typing.Optional[str]
    UrlThumb: typing.Optional[str]
    RelUrlThumb: typing.Optional[str]
    HasOCR: typing.Optional[bool]
    UrlOCR: typing.Optional[str]
    RelUrlOCR: typing.Optional[str]
    UrlOfServerPath: typing.Optional[str]
    RelUrlOfServerPath: typing.Optional[str]
    MimeType: typing.Optional[str]
    IsPublic: typing.Optional[bool]
    Status: typing.Optional[int]
    AvailableThumbs: typing.Optional[typing.List[str]]
    MarkDelete: typing.Optional[bool]
    Privileges: typing.Optional[dict]
    ClientPrivileges: typing.Optional[typing.List[dict]]
    ThumbnailAble: typing.Optional[bool]