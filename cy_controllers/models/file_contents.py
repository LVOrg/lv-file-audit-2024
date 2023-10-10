import typing

from pydantic import BaseModel


class VideoInfoClass(BaseModel):
    Width: typing.Optional[int]
    Height: typing.Optional[int]
    Duration: typing.Optional[int]


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
    VideoInfo: typing.Optional[VideoInfoClass]
    AvailableThumbs: typing.Optional[typing.List[str]]
    MarkDelete: typing.Optional[bool]
    Privileges: typing.Optional[dict]
    ClientPrivileges: typing.Optional[dict]

class ParamFileGetInfo(BaseModel):
    UploadId:str