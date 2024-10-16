import datetime
import gc
import pathlib
import typing
import uuid

import pydantic
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    UploadFile,
    Form, File, Body
)
from starlette.responses import StreamingResponse
from cy_xdoc.auths import Authenticate
import cyx.db_models.files

from cyx.common.msg import MessageService
import mimetypes
router = APIRouter()
controller = Controller(router)
import cy_docs
import cyx.common.msg
from cy_controllers.models import (
    files as controller_model_files
)
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import CheckoutResource
import cy_web
from cyx.repository import Repository
import os
import cyx.common.msg
import bson.errors

@controller.resource()
class FilesSourceController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/{app_name}/files/info",tags=["SOURCE"])
    async def get_info_async(self, app_name: str,
                             UploadId: str = Body(embed=True)) -> controller_model_files.UploadInfoResult:
        """
        APi này lay chi tiet thong tin cua Upload
        :param UploadId:
        :param app_name:
        :return:
        """
        doc_context = Repository.files.app(app_name)
        upload_info = await doc_context.context.find_one_async(
            doc_context.fields.id == UploadId
        )

        if upload_info is None:
            return None
        mt, _ = mimetypes.guess_type(upload_info[doc_context.fields.FileName])
        _thumb_ = False
        if isinstance(mt, str) and (mt.startswith("image/") or mt.startswith("video/")):
            _thumb_ = True
        upload_info.UploadId = upload_info._id
        upload_info.HasOCR = upload_info.OCRFileId is not None
        upload_info.RelUrl = f"api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.FullUrl = f"{cy_web.get_host_url(self.request)}/api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.HasThumb = upload_info.ThumbFileId is not None or _thumb_
        available_thumbs = upload_info.AvailableThumbs or []
        upload_info.AvailableThumbs = []
        for x in available_thumbs:
            upload_info.AvailableThumbs += [f"api/{app_name}/{x}"]
        if upload_info.HasThumb:
            """
            http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
            """
            upload_info.RelUrlThumb = f"api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
            upload_info.UrlThumb = f"{cy_web.get_host_url(self.request)}/api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
        if upload_info.HasOCR:
            """
            http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
            """
            upload_info.RelUrlOCR = f"api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
            upload_info.UrlOCR = f"{cy_web.get_host_url(self.request)}/api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
        if upload_info.VideoResolutionWidth:
            upload_info.VideoInfo = cy_docs.DocumentObject()
            upload_info.VideoInfo.Width = upload_info.VideoResolutionWidth
            upload_info.VideoInfo.Height = upload_info.VideoResolutionHeight
            upload_info.VideoInfo.Duration = upload_info.VideoDuration
        if upload_info.ClientPrivileges and not isinstance(upload_info.ClientPrivileges, list):
            upload_info.ClientPrivileges = [upload_info.ClientPrivileges]
        if upload_info.ClientPrivileges is None:
            upload_info.ClientPrivileges = []
        # if upload_info[doc_context.fields.RemoteUrl]:
        #     upload_info[cy_docs.fields.FullUrl] = upload_info[doc_context.fields.RemoteUrl]
        data = await self.search_engine.get_doc_async(
            app_name=app_name,
            id=UploadId
        )
        search = {}
        if data:
            if data.source and data.source.data_item:
                search["FileName"] = data.source.data_item.FileName
            if data.source and data.source.privileges:
                search["Privileges"] = data.source.privileges
        upload_info.Search = search

        return upload_info.to_pydantic()

    @controller.router.post("/api/files/check_out_source",tags=["SOURCE"])
    async def check_out_source(self, data: CheckoutResource):
        UploadData = self.file_util_service.get_upload(app_name=data.appName,upload_id=data.uploadId)
        if not UploadData:
            raise HTTPException(status_code=404, detail=f"{data.uploadId} not found in {data.appName}")
        file_path = await self.file_util_service.get_physical_path_async(
            app_name=data.appName, upload_id=data.uploadId
        )
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail=f"{data.uploadId} not found in {data.appName}")

        ret = await cy_web.cy_web_x.streaming_async(
            file_path,
            self.request, "application/octet-stream", streaming_buffering=1024 * 4 * 3 * 8
        )

        ret.headers["Content-Disposition"] = f"attachment; filename={data.uploadId}"

        return ret


    @controller.router.post("/api/files/check_in_source",tags=["SOURCE"])
    async def check_in_source(self, appName: str = Body(embed=True), uploadId: str = Body(embed=True),
                              content: UploadFile = File(...)):

        UploadData = self.file_util_service.get_upload(app_name=appName, upload_id=uploadId)
        if not UploadData:
            raise HTTPException(status_code=404, detail=f"{uploadId} not found in {appName}")
        file_path = await self.file_util_service.get_physical_path_async(app_name=appName, upload_id=uploadId)
        with open(file_path, "wb") as f:
            while contents := content.file.read(1024 * 1024):
                f.write(contents)
            self.content_manager_service.remove_check_out(
                app_name=appName,
                upload_id=uploadId,
                client_mac_address=self.request.headers.get('mac_address_id')

            )
            self.raise_re_do_message(
                file_path=file_path,
                app_name=appName,
                data=UploadData
            )
            return dict(message="Update is Ok")


    def raise_re_do_message(self, file_path, app_name, data):
        self.broker.emit(
            app_name=app_name,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT,
            data=data
        )
        root, _, files = list(os.walk(pathlib.Path(file_path).parent.__str__()))[0]
        if data[Repository.files.fields.DocType] == "Image":
            for x in files:
                fx = os.path.join(root, x)
                if pathlib.Path(fx).suffix == ".webp" and pathlib.Path(fx).stem.isnumeric():
                    try:
                        os.remove(fx)
                    except:
                        continue

    @controller.router.post("/api/{app_name}/files/inspect-content",tags=["SOURCE"])
    async def inspect_content_async(self, app_name: str,
                                    UploadId: str = Body(embed=True)):
        try:
            upload_data = await Repository.files.app(app_name).context.find_one_async(
                Repository.files.fields.id == UploadId
            )
            if upload_data is None:
                raise HTTPException(status_code=404, detail=f"{UploadId} not found in {app_name}")
            if isinstance(upload_data.MainFileId, str) and upload_data.MainFileId.startswith("local://"):
                file_path = os.path.join(self.config.file_storage_path, upload_data.MainFileId.split("://")[1])
                is_image = mimetypes.guess_type(file_path)[0].startswith("image/")
                if is_image:
                    Question = "get all text in image"
                    try:
                        text = self.gemini_service.image_prompt(file_path, question=Question)
                    except Exception as e:
                        return dict(
                            error=dict(
                                code="gemini-error",
                                description=f"Gemini-Error:{e}"
                            )
                        )
                    return dict(
                        content=text
                    )
                else:

                    try:
                        text = self.gemini_service.get_text_from_tika(file_path)
                    except Exception as e:
                        return dict(
                            error=dict(
                                code="gemini-error",
                                description=f"Gemini-Error:{e}"
                            )
                        )
                    return dict(
                        content=text
                    )
            else:
                return dict(
                    error=dict(
                        code="resource_was_not_found",
                        description=f"{UploadId} not found in {app_name}"
                    )
                )
        except HTTPException as e:
            raise e

        except Exception as e:
            return dict(
                error=dict(
                    code="system",
                    description=str(e)
                )
            )

    @controller.router.post("/api/{app_name}/files/gemini-assistant",tags=["SOURCE"])
    async def gemini_assistant_async(self, app_name: str,
                                     UploadId: str = Body(embed=True),
                                     Question: str = Body(embed=True)):
        try:
            upload_data = await Repository.files.app(app_name).context.find_one_async(
                Repository.files.fields.id == UploadId
            )
            if upload_data is None:
                raise HTTPException(status_code=404, detail=f"{UploadId} not found in {app_name}")
            if isinstance(upload_data.MainFileId, str) and upload_data.MainFileId.startswith("local://"):
                file_path = os.path.join(self.config.file_storage_path, upload_data.MainFileId.split("://")[1])
                is_image = mimetypes.guess_type(file_path)[0].startswith("image/")
                if is_image:
                    try:
                        text = self.gemini_service.image_prompt(file_path, question=Question)
                    except Exception as e:
                        return dict(
                            error=dict(
                                code="gemini-error",
                                description=f"Gemini-Error:{e}"
                            )
                        )
                    return dict(
                        content=text
                    )
                else:
                    try:
                        text = self.gemini_service.text_prompt(file_path, question=Question)
                    except Exception as e:
                        return dict(
                            error=dict(
                                code="gemini-error",
                                description=f"Gemini-Error:{e}"
                            )
                        )
                    return dict(
                        content=text
                    )
            else:
                return dict(
                    error=dict(
                        code="resource_was_not_found",
                        description=f"{UploadId} not found in {app_name}"
                    )
                )
        except HTTPException as e:
            raise e

        except Exception as e:
            return dict(
                error=dict(
                    code="system",
                    description=str(e)
                )
            )


