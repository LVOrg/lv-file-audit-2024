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


from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
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


from cy_controllers.models.files import SkipFileProcessingOptions


@controller.resource()
class FilesRegisterController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.route.post(
        "/api/{app_name}/files/register", summary="register Upload file"
    )
    async def register_async(self,
                             app_name: str,
                             Data: RegisterUploadInfo,
                             SkipOptions: typing.Optional[SkipFileProcessingOptions] = None) -> typing.Optional[
        RegisterUploadInfoResult]:
        """
            <p>
            <b>
            For a certain pair of Application and  Access Token, before upload any file. Thou must call this api with post data looks like :<br>
             <code>
                {\n
                   Data: { \n
                            FileName: <original client file name only when user upload>,\n
                            ChunkSizeInKB: < a certain file content will be split into many chunks, each chunk has size was limit in this argument >,\n
                            FileSize: <The real certain file size when end user upload>,\n
                            IsPublic: <true if anyone can access the content of file, false: just someone who can access the content of file with their privileges >,\n
                            ThumbConstraints: <This is an optional param, the value looks like '100,200,400,800'.
                                                The service will generate list of thumbnails in those size constraints in list of squares looks like 100x100, 200x200,400x400,800x800  >,\n
                             Privileges: <This is an optional param. This is a list of tags. Each tag is a pair of Type and Values.
                                            (   1- Type is an object type. Thou could set any text value for thy desire.
                                                2- Values is a text which describe a list of values separated by comma.
                                             )
                                            Those looks like: [
                                                                    {
                                                                        Type: 'departemts',
                                                                        Values: 'accounting,hr'
                                                                    },
                                                                    ...
                                                                    {
                                                                        Type:'teams',
                                                                        Values:'codx,sale,marketing'
                                                                    },
                                                                    {
                                                                        Type:'position',
                                                                        Values:' director, team-leader, staff'
                                                                    }

                                                                ] >
                        }
                }
             </code>
             </b>
            </p>
            :param app_name: Ứng dụng nào cần đăng ký Upload
            :param Data: Thông tin đăng ký Upload
            :param token:
            :return:
            """
        request_user = self.memcache_service.get_dict("request_user")

        # async with semaphore:
        #     if request_user is None:
        #         request_user = {}
        #     request_count = request_user.get(self.request.client.host, 0)
        #     if request_count >= MAX_REQUESTS_UPLOAD_FILES:
        #         return JSONResponse(
        #             {
        #                 "code": "Exceed limit request",
        #                 "message": "Upstream: too many requests"
        #             }, status_code=429
        #         )
        #     request_user[self.request.client.host] = request_count + 1
        #     self.memcache_service.set_dict("request_user", request_user)

        if Data.storageType is None or Data.storageType not in ["onedrive", "local"]:
            ret_quit = RegisterUploadInfoResult()
            ret_quit.Error = Error()
            ret_quit.Error.Message = f"Missing field storageType. storageType must be local or onedrive"
            ret_quit.Error.Code = "MissingField"
            return ret_quit
        if Data.storageType == "onedrive":
            try:
                self.fucking_azure_account_service.acquire_token(
                    app_name=app_name
                )
            except FuckingWhoreMSApiCallException as e:
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = e.message
                ret_quit.Error.Code = e.code
                return ret_quit
        privileges = Data.Privileges
        skip_option = {}
        if SkipOptions:
            skip_option = SkipOptions.dict()
        try:
            ret = await self.file_service.add_new_upload_info_async(
                app_name=app_name,
                chunk_size=Data.ChunkSizeInKB * 1024,
                file_size=Data.FileSize,
                client_file_name=Data.FileName,
                is_public=Data.IsPublic,
                thumbs_support=Data.ThumbConstraints,
                web_host_root_url=cy_web.get_host_url(),
                privileges_type=privileges,
                meta_data=Data.meta_data,
                skip_option=skip_option,
                storage_type=Data.storageType,
                onedriveScope=Data.onedriveScope

            )
            ret_data = RegisterUploadInfoResult(Data=ret.to_pydantic())
            return ret_data
        except Exception as ex:
            self.logger_service.error(ex)
            ret_data = RegisterUploadInfoResult()
            ret_data.Error = Error(
                Code="system",
                Message="Unknown error at server"
            )
            return ret_data
