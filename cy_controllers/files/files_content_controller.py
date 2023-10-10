from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)
from cy_controllers.models.file_contents import (
    UploadInfoResult,ParamFileGetInfo
)
import fastapi.requests
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse,mimetypes
)
router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
@controller.resource()
class FilesContentController(BaseController):


    @controller.route.get(
        "/api/{app_name}/files/test", summary="Upload file"
    )
    async def test(self,app_name:str)->str:
        self.logger_service.info(app_name)

        return  "OK"
    @controller.router.get(
        "/api/{app_name}/thumb/{directory:path}"
    )
    async def get_thumb(self,app_name: str, directory: str):
        """
        Xem hoặc tải nội dung file
        :param directory:
        :param app_name:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)

        thumb_dir_cache = self.file_cacher_service.get_path(os.path.join(app_name, "thumbs"))
        cache_thumb_path = cy_web.cache_content_check(thumb_dir_cache, directory.lower().replace("/", "_"))
        if cache_thumb_path:
            return FileResponse(cache_thumb_path)

        upload_id = directory.split('/')[0]
        fs = await self.file_service.get_main_main_thumb_file_async(app_name, upload_id)
        self.file_service.db_connect.db(app_name)
        if fs is None:
            return Response(
                status_code=404
            )
        content = fs.read(fs.get_size())
        fs.seek(0)
        cy_web.cache_content(thumb_dir_cache, directory.replace('/', '_'), content)
        del content
        mime_type, _ = mimetypes.guess_type(directory)
        ret = await cy_web.cy_web_x.streaming_async(fs, self.request, mime_type)
        return ret

    @controller.router.get(
        "/api/{app_name}/file/{directory:path}"
    )
    async def get_content(self,app_name: str, directory: str):
        cache_dir = self.file_cacher_service.get_path(os.path.join(app_name, "images"))

        upload_id = directory.split('/')[0]
        upload = self.file_service.get_upload_register(app_name, upload_id)
        if upload is None:
            from fastapi import Response
            response = Response(content="Resource not found", status_code=404)
            return response
        if not upload.IsPublic:
            await self.auth_service.check_request(app_name, self.request)
        mime_type, _ = mimetypes.guess_type(directory)
        if mime_type.startswith('image/'):

            file_cache = cy_web.cache_content_check(cache_dir, directory.replace('/', '_'))
            if file_cache:
                return FileResponse(path=file_cache)

        runtime_file_reader = None
        # upload.IsPublic= False

        # if upload and upload.FileModuleController:
        #     try:
        #         runtime_file_reader = cy_kit.singleton_from_path(upload.FileModuleController)
        #     except ModuleNotFoundError as e:
        #         runtime_file_reader = None

        fs = self.file_service.get_main_file_of_upload_by_rel_file_path(
            app_name=app_name,
            rel_file_path=directory,
            runtime_file_reader=runtime_file_reader
        )

        if fs is None:
            fs = self.file_service.get_main_file_of_upload(
                app_name=app_name,
                upload_id=upload_id
            )

        if fs is None:
            from fastapi.responses import Response
            return Response(status_code=401)
        if mime_type.startswith('image/'):
            content = fs.read(fs.get_size())
            fs.seek(0)
            cy_web.cache_content(cache_dir, directory.replace('/', '_'), content)
            del content
        mime_type, _ = mimetypes.guess_type(directory)
        if hasattr(fs, "cursor_len"):
            setattr(fs, "cursor_len", self.config.content_segment_len)
        ret = await cy_web.cy_web_x.streaming_async(
            fs, self.request, mime_type, streaming_buffering=1024 * 4 * 3 * 8
        )
        if self.request.query_params.get('download') is not None:
            import urllib

            file_name_form_url = self.request.url.path.split('/')[self.request.url.path.split('/').__len__() - 1]
            file_name_form_url = urllib.parse.quote(file_name_form_url)
            ret.headers["Content-Disposition"] = f"attachment; filename={file_name_form_url}"
        return ret


    @controller.router.get("/api/{app_name}/thumbs/{directory:path}")
    async def get_thumb_of_files(self,app_name: str, directory: str):
        """
        Xem hoặc tải nội dung file
        :param app_name:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)

        thumb_dir_cache = self.file_cacher_service.get_path(os.path.join(app_name, "custom_thumbs"))
        cache_thumb_path = cy_web.cache_content_check(thumb_dir_cache, directory.lower().replace("/", "_"))
        if cache_thumb_path:
            return FileResponse(cache_thumb_path)

        fs = self.file_storage_service.get_file_by_name(
            app_name=app_name,
            rel_file_path=f"thumbs/{directory}"
        )
        if fs is None:
            """
            Allow original thumb if custom size thumb not avalaable
            Modified on: 01-05-2023
            """
            thumb_dir_cache = os.path.join(app_name, "custom_thumbs")
            cache_thumb_path = cy_web.cache_content_check(thumb_dir_cache, directory.lower().replace("/", "_"))
            if cache_thumb_path:
                return FileResponse(cache_thumb_path)

            upload_id = directory.split('/')[0]


            fs = self.file_service.get_main_main_thumb_file(app_name, upload_id)
            if fs is None:
                return Response(
                    status_code=401
                )
            content = fs.read(fs.get_size())
            fs.seek(0)
            cy_web.cache_content(thumb_dir_cache, directory.replace('/', '_'), content)
            del content
            mime_type, _ = mimetypes.guess_type(directory)
            ret = await cy_web.cy_web_x.streaming_async(fs, self.request, mime_type)
            return ret
        content = fs.read(fs.get_size())
        fs.seek(0)
        cy_web.cache_content(thumb_dir_cache, directory.replace('/', '_'), content)
        del content
        mime_type, _ = mimetypes.guess_type(directory)
        ret = await cy_web.cy_web_x.streaming_async(fs, self.request, mime_type)
        return ret

    @controller.router.post("/api/{app_name}/files/info")
    def get_info(self,app_name: str, data: ParamFileGetInfo=Body(...)) -> UploadInfoResult:
        """
        APi này lay chi tiet thong tin cua Upload
        :param app_name:
        :return:
        """
        UploadId=data.UploadId
        doc_context = self.file_service.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        upload_info = doc_context.context @ UploadId
        if upload_info is None:
            return None
        upload_info.UploadId = upload_info._id
        upload_info.HasOCR = upload_info.OCRFileId is not None
        upload_info.RelUrl = f"api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.FullUrl = f"{cy_web.get_host_url()}/api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.HasThumb = upload_info.ThumbFileId is not None
        available_thumbs = upload_info.AvailableThumbs or []
        upload_info.AvailableThumbs = []
        for x in available_thumbs:
            upload_info.AvailableThumbs += [f"api/{app_name}/{x}"]
        if upload_info.HasThumb:
            """
            http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
            """
            upload_info.RelUrlThumb = f"api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
            upload_info.UrlThumb = f"{cy_web.get_host_url()}/api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
        if upload_info.HasOCR:
            """
            http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
            """
            upload_info.RelUrlOCR = f"api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
            upload_info.UrlOCR = f"{cy_web.get_host_url()}/api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
        if upload_info.VideoResolutionWidth:
            upload_info.VideoInfo = cy_docs.DocumentObject()
            upload_info.VideoInfo.Width = upload_info.VideoResolutionWidth
            upload_info.VideoInfo.Height = upload_info.VideoResolutionHeight
            upload_info.VideoInfo.Duration = upload_info.VideoDuration
        if upload_info.ClientPrivileges and not isinstance(upload_info.ClientPrivileges, list):
            upload_info.ClientPrivileges = [upload_info.ClientPrivileges]
        if upload_info.ClientPrivileges is None:
            upload_info.ClientPrivileges = []
        return upload_info.to_pydantic()