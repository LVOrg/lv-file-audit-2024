import typing

from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body,
    UploadFile,
    File

)

import cyx.common.msg
from cy_controllers.models.file_contents import (
    UploadInfoResult, ParamFileGetInfo, ReadableParam
)
import fastapi.requests
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse, mimetypes
)

router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
import urllib
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException, call_ms_func
from cy_fucking_whore_microsoft.fucking_models.one_drive import (
    BullShitError, GetListFolderResult,
    GetQuotaInfo, GetQuotaResult,
    RegisterUploadResult, RegisterUploadResultInfo
)

from cy_xdoc.auths import Authenticate
@controller.resource()
class FuckingOneDriveController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.router.post(
        path="/api/{app_name}/onedrive/folder/list/{folder_id:path}"
    )
    async def one_drive_folder_list(self,app_name:str,folder_id:str):
        ret = GetListFolderResult()
        if '/' in folder_id:
            folder_id=folder_id.replace("/",":/")+":"
        try:
            token = self.fucking_azure_account_service.acquire_token(
                app_name=app_name
            )
            data = call_ms_func(
                method="get",
                api_url=f"drive/{folder_id}/children?includeHiddenFolders=true&$filter=folder ne null",
                token=token,
                body=None,
                return_type=dict,
                request_content_type="application/json"
            )
            ret.data = data.get("value",[])
            ret.total = data.get("@odata.count",0)
            return ret
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(
                code= e.code,
                message = e.message
            )
            return ret
    @controller.router.post(
        path="/api/{app_name}/onedrive/get_quota"
    )
    async def get_quota(self,app_name)->GetQuotaResult:
        ret = GetQuotaResult()
        try:
            drive_info = self.fucking_azure_onedrive_service.get_drive_info(
                app_name=app_name
            )
            ret.data = GetQuotaInfo()
            ret.data.driveType= drive_info.driveType
            ret.data.remainingInBytes = drive_info.remaining
            ret.data.totalInBytes = drive_info.total
            ret.data.remainingInGB = drive_info.remaining/(1024**3)
            ret.data.totalInGB = drive_info.total / (1024 ** 3)
            return ret

        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(
                code = e.code,
                message = e.message
            )
            return ret
    @controller.router.post(
        path="/api/{app_name}/onedrive/files/upload"
    )
    async def do_upload(self,
                        app_name:str,

                        fileChunk: UploadFile = File(...),
                        fileSizeInBytes: typing.Optional[int] = Body(embed=True,default=None),
                        chunkIndex: typing.Optional[int] = Body(embed=True,default=None)
                        )->typing.Union[RegisterUploadResult,str]:
        ret= RegisterUploadResult()
        try:
            fucking_onedrive_root_folder_for_lv_file = self.fucking_azure_onedrive_service.get_root_folder(
                app_name = app_name
            )
            if fileSizeInBytes is None:
                self.fucking_azure_onedrive_service.upload_file(
                    app_name=app_name,
                    file=fileChunk
                )
            return "xong"
        except FuckingWhoreMSApiCallException as e:
            ret.error = BullShitError(
                code = e.code,
                message = e.message
            )
            return ret
