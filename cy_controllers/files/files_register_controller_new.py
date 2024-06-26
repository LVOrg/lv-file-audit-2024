import datetime
import os.path
import uuid
import pymongo.errors
from cyx.repository import Repository
from cy_controllers.common.base_controller import (
    BaseController,
    Authenticate,
    APIRouter,
    Controller,
    Depends

)
import cy_web
import typing
from pydantic import BaseModel
from fastapi.responses import Response, JSONResponse

router = APIRouter()
controller = Controller(router)


class PrivilegesType(BaseModel):
    Type: str
    Values: str
    """
    Separated by comma
    """


class RegisterUploadInfo(BaseModel):
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


class RequestRegisterUploadInfo(BaseModel):
    Data: RegisterUploadInfo
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
                             Data: RegisterUploadInfo,
                             SkipOptions: typing.Optional[SkipFileProcessingOptions] = None):
        if Data.UploadId is None:
            if Data.storageType is None or Data.storageType=="local":
                ret = await self.file_util_service.register_new_upload_local_async(
                    app_name=app_name,
                    from_host =cy_web.get_host_url(self.request),
                    data= Data.json()

                )
                return ret
            elif Data.storageType=="google-drive":
                ret = await self.file_util_service.register_new_upload_google_drive_async(
                    app_name=app_name,
                    from_host=cy_web.get_host_url(self.request),
                    data=Data.json()

                )
                return ret
            elif Data.storageType=="onedrive":
                ret = await self.file_util_service.register_new_upload_one_drive_async(
                    app_name=app_name,
                    from_host= cy_web.get_host_url(self.request),
                    data=Data.json()

                )
                return ret
        else:
            if Data.storageType is None or Data.storageType == "local":
                ret = await self.file_util_service.update_upload_local_async(
                    app_name=app_name,
                    data=Data.json()

                )
                return ret
            elif Data.storageType == "google-drive":
                ret = await self.file_util_service.update_google_drive_async(
                    app_name=app_name,
                    from_host=cy_web.get_host_url(self.request),
                    data=Data.json()

                )
                return ret
            elif Data.storageType == "onedrive":
                ret = await self.file_util_service.update_upload_one_drive_async(
                    app_name=app_name,
                    data=Data.json(),
                    from_host =  cy_web.get_host_url(self.request)

                )
                return ret



