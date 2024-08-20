import datetime
import os.path
import uuid
import pymongo.errors
from cyx.repository import Repository
from cy_controllers.common.base_controller import BaseController
from fastapi import APIRouter, Depends
from cy_xdoc.auths import Authenticate
from fastapi_router_controller import Controller
import cy_web
import typing
from pydantic import BaseModel
router = APIRouter()
controller = Controller(router)

class PrivilegesType(BaseModel):
    Type: str
    Values: str
    """
    Separated by comma
    """


class RegisterUploadInfoNew(BaseModel):
    """
    Bảng ghi thông tin đăng ký upload
    """
    FileName: str
    ChunkSizeInKB: int
    FileSize: int
    IsPublic: typing.Optional[bool]
    ThumbConstraints: typing.Optional[str]
    Privileges: typing.Optional[typing.List[PrivilegesType]]
    meta_data: typing.Optional[dict]
    storageType: typing.Optional[str]
    onedriveScope: typing.Optional[str]
    onedriveExpiration: typing.Optional[datetime.datetime]
    onedrivePassword: typing.Optional[str]
    encryptContent: typing.Optional[bool]
    googlePath: typing.Optional[str]
    UploadId:typing.Optional[str]


class RegisterUploadResult(BaseModel):
    NumOfChunks: int
    """
    Số phân đoạn: Rất quan trọng dùng để hỗ trợ __client__ upload 
    """
    ChunkSizeInBytes: int
    """
    Kích thước phân đoạn: Rất quan trọng dùng để hỗ trợ __client__ upload
    """
    UploadId: str
    """
    Upload Id: Hỗ trơ các ứng dụng khác lấy thông tin
    """
    ServerFilePath: str
    """
    Đường dẫn đến file tại server: Rất quan trọng các ứng dụng khác sẽ lưu lại thông tin này
    """
    MimeType: str
    """
    Mime type:: Rất quan trọng các ứng dụng khác sẽ lưu lại thông tin này
    """
    RelUrlOfServerPath: str
    SizeInHumanReadable: str
    UrlOfServerPath: str
    OriginalFileName: str
    """
    Tên file gốc lúc upload
    """
    UrlThumb: str
    """
    Đường dẫn đầy đủ đến ảnh Thumb
    """
    RelUrlThumb: str
    FileSize: int
    SearchEngineInsertTimeInSecond: float


class Error(BaseModel):
    """
    Thông tin chi tiết của lỗi
    """
    Code: str | None
    Message: str | None
    Fields: typing.List[str] | None



import asyncio

MAX_REQUESTS_UPLOAD_FILES = 2
semaphore = asyncio.Semaphore(MAX_REQUESTS_UPLOAD_FILES)


class RegisterUploadInfoResult(BaseModel):
    """
    Bảng ghi cấu trúc trả vể cho API upload
    """
    Data: typing.Optional[RegisterUploadResult]
    Error: typing.Optional[Error]


class RequestRegisterUploadInfoNew(BaseModel):
    Data: RegisterUploadInfoNew
from cyx.common import config

from cy_controllers.models.files import SkipFileProcessingOptions
version2 = config.generation if hasattr(config,"generation") else None

@controller.resource()
class FilesRegisterControllerNew(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.route.post(
        "/api/{app_name}/files/register" if version2 else "/api/{app_name}/files/register_new", summary="register Upload file", tags=["FILES"]
    )
    async def register_async(self,
                             app_name: str,
                             Data: RegisterUploadInfoNew,
                             SkipOptions: typing.Optional[SkipFileProcessingOptions] = None):
        ret = await self.file_util_service.register_upload_async(
            app_name=app_name,
            register_data=Data.__dict__,
            from_host=cy_web.get_host_url(self.request)

        )
        return ret



