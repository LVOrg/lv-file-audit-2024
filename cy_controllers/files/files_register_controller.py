import datetime
import os.path
import pathlib
import traceback
import uuid
import pymongo.errors
from cyx.repository import Repository
from fastapi import APIRouter,Depends
from fastapi_router_controller import Controller
from cy_xdoc.auths import Authenticate
from cy_controllers.common.base_controller import BaseController
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
    UploadId: typing.Optional[str]


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

version2 = config.generation if hasattr(config, "generation") else None


@controller.resource()
class FilesRegisterController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.route.post(
        "/api/{app_name}/files/register" if not version2 else "/api/{app_name}/files/register_old",
        summary="register Upload file", tags=["FILES"]
    )
    async def register_async(self,
                             app_name: str,
                             Data: RegisterUploadInfo,
                             SkipOptions: typing.Optional[SkipFileProcessingOptions] = None):
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
        self.malloc_service.reduce_memory()
        if Data.UploadId and Data.UploadId != "":
            upload_item = self.file_util_service.get_upload(
                app_name=app_name,
                upload_id=Data.UploadId,
                cache=False
            )
            if not upload_item:
                return dict(
                    Error=dict(
                        Code="ResourceNotFound",
                        Message="Resource was not found"
                    )
                )
            return await self.file_util_service.register_upload_async(
                app_name=app_name,
                register_data=Data.__dict__,
                from_host=cy_web.get_host_url(self.request)
            )
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
            if not self.cloud_service_utils.is_ready_for(app_name=app_name, cloud_name="Azure"):
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = f"Azure did not bestow for {app_name}"
                ret_quit.Error.Code = "AzureWasNotReady"
                return ret_quit

        if Data.storageType == "google-drive":
            if not self.cloud_service_utils.is_ready_for(app_name=app_name, cloud_name="Google"):
                ret_quit = RegisterUploadInfoResult()
                ret_quit.Error = Error()
                ret_quit.Error.Message = f"Google did not bestow for {app_name}"
                ret_quit.Error.Code = "GoogleWasNotReady"
                return ret_quit
            if Data.googlePath is None or len(Data.googlePath) == 0:
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
                if total_space < Data.FileSize:
                    ret_quit = RegisterUploadInfoResult()
                    ret_quit.Error = Error()
                    ret_quit.Error.Message = "Not enough space to do that"
                    ret_quit.Error.Code = "NotEnoughSpace"
                    return ret_quit
                Data.googlePath = Data.googlePath.lstrip('/').rstrip('/').replace('//', '/')
                checkpath = os.path.join(Data.googlePath, Data.FileName)
                new_id = str(uuid.uuid4())
                Data.FileName = await self.inc_version_of_file_name_if_duplicate_async(
                    app_name=app_name,
                    upload_id = new_id,
                    full_path_on_cloud = checkpath,
                    client_file_name = Data.FileName
                )

                        # ret_quit = RegisterUploadInfoResult()
                        # ret_quit.Error = Error()
                        # ret_quit.Error.Message = f"{checkpath} is existing"
                        # ret_quit.Error.Code = "FileIsExisting"
                        # return ret_quit

        privileges = Data.Privileges
        skip_option = {}
        if SkipOptions:
            skip_option = SkipOptions.dict()
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
            url_google_upload=url_google_upload,
            google_file_id=google_file_id,
            google_folder_id=folder_id,
            google_folder_path=Data.googlePath,
            version=1

        )
        ret_data = RegisterUploadInfoResult(Data=ret.to_pydantic())
        return ret_data

    async def inc_version_of_file_name_if_duplicate_async(self, app_name, upload_id, full_path_on_cloud,
                                                          client_file_name):

        async def insert_async(_app,__path,__id,__client_file_name):
            await  Repository.files.app(_app).context.insert_one_async(
                Repository.files.fields.id << __id,
                Repository.files.fields.FullPathOnCloud << __path
            )
            return __client_file_name
        async def insert_and_change_file_name_if_dup_async(_app,_path,_id,_client_file_name):
            ok =False
            original_path = _path.encode().decode()
            ret_file_name = _client_file_name.encode().decode()
            while not ok:
                try:
                    await insert_async(_app, _path, _id, ret_file_name)
                    return ret_file_name
                except pymongo.errors.DuplicateKeyError as ex:

                    if (hasattr(ex, "details") and
                            isinstance(ex.details, dict) and
                            ex.details.get('keyPattern', {}).get(Repository.files.fields.FullPathOnCloud.__name__) == 1
                    ):
                        await Repository.duplicate_file_history.app(_app).context.insert_one_async(
                            Repository.duplicate_file_history.fields.FullFilePath << original_path
                        )
                        num_of_doc = Repository.duplicate_file_history.app(_app).context.count(
                            Repository.duplicate_file_history.fields.FullFilePath == original_path
                        )
                        client_file_name_only = pathlib.Path(_client_file_name).stem
                        ext_file = pathlib.Path(_client_file_name).suffix
                        if ext_file:
                            ret_file_name = f"{client_file_name_only}({num_of_doc}){ext_file}"
                        else:
                            ret_file_name = f"{client_file_name_only}({num_of_doc})"
                        _path = f"{pathlib.Path(_path).parent.__str__()}/{ret_file_name}"
                        # ret = await insert_async(_app, _path, _id, ret_file_name)

                        # ok = True
                        # return ret_file_name
        try:
            ret = await insert_and_change_file_name_if_dup_async(app_name,full_path_on_cloud,upload_id,client_file_name)
            return ret
        except:
            print(traceback.format_exc())
            print("error")