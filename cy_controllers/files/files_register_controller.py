import datetime

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
        "/api/{app_name}/files/register", summary="register Upload file",tags=["FILES"]
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
        url_google_upload, google_file_id = None, None
        folder_id = None
        Data.storageType = Data.storageType or "local"
        """
        Default encrypt content is settings True
        """
        Data.encryptContent = Data.encryptContent or True
        if Data.storageType is None or Data.storageType not in ["onedrive", "local", "google-drive"]:
            ret_quit = RegisterUploadInfoResult()
            ret_quit.Error = Error()
            ret_quit.Error.Message = f"Missing field storageType. storageType must be local,onedrive or google-drive"
            ret_quit.Error.Code = "MissingField"
            return ret_quit
        if Data.storageType == "onedrive":
            if not self.cloud_service_utils.is_ready_for(app_name=app_name,cloud_name="Azure"):
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = f"Azure did not bestow for {app_name}"
                ret_quit.Error.Code = "AzureWasNotReady"
                return ret_quit


        if Data.storageType == "google-drive":
            if not self.cloud_service_utils.is_ready_for(app_name=app_name,cloud_name="Google"):
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = f"Google did not bestow for {app_name}"
                ret_quit.Error.Code = "GoogleWasNotReady"
                return ret_quit
            if Data.googlePath is None or len(Data.googlePath)==0:
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = f"Google drive upload require googlePath field"
                ret_quit.Error.Code = "MissField"
                return ret_quit
            else:
                total_space, error = self.cloud_service_utils.drive_service.get_available_space(
                    app_name=app_name,
                    cloud_name="Google"
                )
                if error:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = error.get("Message")
                    ret_quit.Error.Code = error.get("Code")
                    return ret_quit
                if total_space< Data.FileSize:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = "Not enough space to do that"
                    ret_quit.Error.Code = "NotEnoughSpace"
                    return ret_quit

                is_exist,folder_id, error= self.google_directory_service.check_before_upload(
                    app_name=app_name,
                    directory = Data.googlePath,
                    file_name= Data.FileName)
                if error:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = error.get("Message")
                    ret_quit.Error.Code = error.get("Code")
                    return ret_quit
                if is_exist:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = f"{Data.googlePath}/{Data.FileName} is already in Google drive"
                    ret_quit.Error.Code = "DuplicateFile"
                    return ret_quit
                else:
                    google_file_id,url_google_upload,error = self.google_directory_service.register_upload_file(
                        app_name=app_name,
                        directory_id = folder_id,
                        file_name= Data.FileName,
                        file_size=  Data.FileSize
                    )
                    if error:
                        ret_quit = RegisterUploadInfoResult()
                        ret_quit.Error = Error()
                        ret_quit.Error.Message = error["Message"]
                        ret_quit.Error.Code = error["Code"]
                        return ret_quit
                    else:
                        self.google_directory_service.make_map_file(app_name=app_name,directory=Data.googlePath,filename= Data.FileName,google_file_id= google_file_id)

            try:
                client_id, secret_key, _, error = self.g_drive_service.get_id_and_secret(
                    app_name=app_name
                )
                if isinstance(error,dict):
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = error.get("Message")
                    ret_quit.Error.Code = error.get("Code")
                    return ret_quit
                if client_id is None:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = f"Tenant {app_name} did not set. The bestows is deny."
                    ret_quit.Error.Code = "MissSettings"
                    return ret_quit
                Data.encryptContent = True
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
                web_host_root_url=cy_web.get_host_url(self.request),
                privileges_type=privileges,
                meta_data=Data.meta_data,
                skip_option=skip_option,
                storage_type=Data.storageType,
                onedriveScope=Data.onedriveScope,
                onedrive_password=Data.onedrivePassword,
                onedrive_expiration=Data.onedriveExpiration,
                is_encrypt_content=Data.encryptContent,
                url_google_upload = url_google_upload,
                google_file_id = google_file_id,
                google_folder_id = folder_id

            )
            ret_data = RegisterUploadInfoResult(Data=ret.to_pydantic())
            return ret_data
        except FuckingWhoreMSApiCallException as e:
            ret_data = RegisterUploadInfoResult()
            ret_data.Error = Error(
                Code=e.code,
                Message=e.message
            )
            return ret_data
        except Exception as ex:
            self.logger_service.error(ex)
            ret_data = RegisterUploadInfoResult()
            ret_data.Error = Error(
                Code="system",
                Message=str(ex)
            )
            return ret_data
