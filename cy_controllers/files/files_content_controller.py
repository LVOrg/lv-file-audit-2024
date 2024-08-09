import pathlib
import sys
import traceback
import typing

import bson
from cyx.repository import Repository
from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)
import gridfs.errors
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
import requests.exceptions
router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
from cyx.common import config
# version2 = config.generation if hasattr(config,"generation") else None
version2=None
@controller.resource()
class FilesContentController(BaseController):

    @controller.route.get(
        "/api/{app_name}/files/test", summary="Upload file"
    )
    async def test(self, app_name: str) -> str:
        self.logger_service.info(app_name)

        return "OK"

    @controller.router.get(
        "/api/{app_name}/thumb/{directory:path}"  ,
        tags=["FILES-CONTENT"]
    )
    async def get_thumb(self, app_name: str, directory: str):
        """
        Xem hoặc tải nội dung file
        :param directory:
        :param app_name:
        :return:
        """

        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        upload_id = None
        is_file_not_found = False
        file_path = await self.thumb_service.get_async(app_name,directory,700)
        if file_path is not None:


            ret = await cy_web.cy_web_x.streaming_async(file_path, self.request, "image/webp")
            return ret
            # image_file_path = self.local_file_caching_service.cache_file(
            #     file_path
            # )
            # mt, _ = mimetypes.guess_type(image_file_path)
            # return FileResponse(image_file_path)
        else:
            return Response(
                        status_code=404
                    )



    def get_full_path_of_local_from_cache(self, upload):
        key = f"{self.config.file_storage_path}/{__file__}/{type(self).__name__}/get_full_path_of_local_from_cache/{upload.id}"
        ret = self.memcache_service.get_str(key)
        if ret is None:
            full_path = os.path.join(self.config.file_storage_path, upload.MainFileId[len("local://"):])
            full_path = os.path.join(pathlib.Path(full_path).parent.parent.__str__(), upload.FullFileNameLower)
            if not os.path.isfile(full_path):
                raise FileNotFoundError()
            else:
                self.memcache_service.set_str(key, full_path)
                ret = full_path
        return ret

    @controller.router.get(
        "/api/{app_name}/file/{directory:path}" ,
        tags=["FILES-CONTENT"]
    )
    # async def get_content(self, app_name: str, directory: str):
    #     return await self.file_util_service.get_file_content_async(self.request,app_name,directory)
    async def get_content_from_all(self, app_name: str, directory: str):
        if len(directory.split('/'))>2:
            directory = directory.split('/')[0]+"/"+directory.split('/')[1]
        try:
            return await self.file_util_service.get_file_content_async(request=self.request,app_name=app_name,directory=directory)
        except requests.exceptions.HTTPError as ex:
            return Response(content=ex.response.content,status_code=ex.response.status_code)
        except FileNotFoundError as ex:
            return Response(content="Content was not found", status_code=404)
        except Exception as ex:
            return Response(content="ServerError", status_code=500)
    # @controller.router.get(
    #     "/api/{app_name}/file/{directory:path}" if not version2 else "/api/{app_name}/file-old/{directory:path}"  ,
    #     tags=["FILES-CONTENT"]
    # )
    # async def get_content(self, app_name: str, directory: str):
    #     return await self.file_util_service.get_file_content_async(self.request,app_name,directory)

    async def get_content(self, app_name: str, directory: str):
        # if len(directory.split('/'))>2:
        #     directory = directory.split('/')[0]+"/"+directory.split('/')[1]

        cloud_info = self.cloud_cache_service.get_request_from_cache(app_name=app_name,directory=directory)
        if cloud_info:
            if cloud_info.storage_type=="onedrive":
                return await self.azure_utils_service.get_content_async(
                    app_name=app_name,
                    cloud_file_id=cloud_info.cloud_id,
                    content_type=cloud_info.content_type,
                    request=self.request,
                    upload_id=cloud_info.upload_id,
                    download_only=self.request.query_params.get('download') is not None,

                )
            if cloud_info.storage_type=="google-drive":
                ret = await self.g_drive_service.get_content_async(
                    app_name=app_name,
                    client_file_name=cloud_info.file_name,
                    upload_id=cloud_info.upload_id,
                    cloud_id=cloud_info.cloud_id,
                    request=self.request,
                    content_type=cloud_info.content_type,
                    download_only=self.request.query_params.get('download') is not None
                )
                return ret


        cache_dir = self.file_cacher_service.get_path(os.path.join(app_name, "images"))
        upload_id = directory.split('/')[0]
        upload = self.file_service.get_upload_register_with_cache(app_name, upload_id)

        server_file_path = await self.file_util_service.get_physical_path_async(app_name=app_name,upload_id=upload_id)
        if server_file_path.endswith(".chunks"):
            return await self.file_util_service.get_file_content_async(self.request, app_name, directory)

        if upload is None:
            from fastapi import Response
            response = Response(content="Resource not found", status_code=404)
            return response
        if upload.StorageType == "onedrive":

            upload = Repository.files.app(app_name).context.find_one(Repository.files.fields.Id == upload_id)
            if upload[Repository.files.fields.CloudId] is not None:
                try:
                    m,_ =mimetypes.guess_type(directory)
                    self.cloud_cache_service.cache_request(
                        app_name=app_name,
                        directory=directory,
                        storage_type=upload.StorageType,
                        cloud_id=upload[Repository.files.fields.CloudId],
                        content_type=m,
                        upload_id=upload_id,
                        file_name= upload[Repository.files.fields.FileName]

                    )
                    return await self.azure_utils_service.get_content_async(
                        app_name=app_name,
                        cloud_file_id=upload[Repository.files.fields.CloudId],
                        content_type=m,
                        request=self.request,
                        upload_id= upload_id,
                        download_only=self.request.query_params.get('download') is not None
                    )
                except:
                    from  fastapi.responses import HTMLResponse
                    return HTMLResponse(content=traceback.format_exc(),status_code=500)
                # return self.fucking_azure_onedrive_service.get_content(
                #     app_name=app_name,
                #     upload_id=upload_id,
                #     request=self.request,
                #     client_file_name=upload.FileName
                # )
        if upload.StorageType=="google-drive":
            upload = Repository.files.app(app_name).context.find_one(Repository.files.fields.Id==upload_id)
            if upload[Repository.files.fields.CloudId] is not None:
                m, _ = mimetypes.guess_type(directory)
                self.cloud_cache_service.cache_request(
                    app_name=app_name,
                    directory=directory,
                    storage_type=upload.StorageType,
                    cloud_id=upload[Repository.files.fields.CloudId],
                    content_type=m,
                    upload_id=upload_id,
                    file_name=upload[Repository.files.fields.FileName]

                )
                ret = await self.g_drive_service.get_content_async(
                    app_name=app_name,
                    client_file_name=upload.FileName,
                    upload_id= upload_id,
                    cloud_id= upload[Repository.files.fields.CloudId],
                    request=self.request,
                    content_type=m,
                    download_only=self.request.query_params.get('download') is not None
                )
                return ret
        if not upload.IsPublic:
            if self.request.query_params.get("local-share-id") and self.request.query_params.get("app-name"):
                check_data = self.local_api_service.check_local_share_id(
                    app_name = self.request.query_params.get("app-name"),
                    local_share_id=self.request.query_params.get("local-share-id")
                )
                if check_data and isinstance(check_data.UploadId,str) and check_data.UploadId == upload_id:
                    pass
                else:
                    await self.auth_service.check_request(app_name, self.request)

        mime_type, _ = mimetypes.guess_type(directory)
        if mime_type.startswith('image/') and self.request.headers.get('Range') is None:

            if upload.MainFileId is None:
                upload = Repository.files.app(app_name).context.find_one_async(
                    Repository.files.fields.id==upload_id
                )
            if upload.MainFileId.startswith("local://"):
                if hasattr(self.config, "file_storage_path"):
                    full_path = self.get_full_path_of_local_from_cache(upload)
                    if isinstance(mime_type, str):
                        return FileResponse(path=full_path, media_type=mime_type)
                    else:
                        return FileResponse(path=full_path)
        runtime_file_reader = None


        fs = self.file_service.get_main_file_of_upload_by_rel_file_path(
            app_name=app_name,
            rel_file_path=upload.FullFileNameLower,
            runtime_file_reader=runtime_file_reader
        )
        if fs is None:
            rel_path = os.path.join(directory.split('/')[0], upload.FullFileNameLower.split('/')[-1])
            fs = self.file_service.get_main_file_of_upload(
                app_name=app_name,
                upload_id=rel_path
            )

        if fs is None:
            from fastapi.responses import Response
            return Response(status_code=401)
        if mime_type.startswith('image/'):

            import inspect
            if inspect.iscoroutinefunction(fs.read):
                content = await fs.read(fs.get_size())
            else:
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



    @controller.router.get("/api/{app_name}/thumbs/{directory:path}" ,tags=["FILES-CONTENT"])
    async def get_thumb_of_files(self, app_name: str, directory: str):
        """
        Xem hoặc tải nội dung file
        :param app_name:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        if not directory.split('/')[-1].split('.')[0].isnumeric():
            raise ValueError(f"{directory} must be end with number")
        size= int(directory.split('/')[-1].split('.')[0])
        file_path = await self.thumb_service.get_async(app_name, directory, size)
        if isinstance(file_path,bson.ObjectId):
            fs= self.file_util_service.get_fs_mongo(app_name,file_id=file_path)
            ret = await cy_web.cy_web_x.streaming_async(fs, self.request, "image/webp")
            return ret


        if file_path is not None:

            ret = await cy_web.cy_web_x.streaming_async(file_path, self.request, "image/webp")
            return ret

        else:
            return Response(
                status_code=404
            )


    @controller.router.post("/api/{app_name}/content/readable",tags=["FILES-CONTENT"])
    def get_content_readable(
            self,
            app_name: str,
            data: ReadableParam = Body(...)):
        """
        This api get <br/>
        chỉ nhận nội dung tải lên theo id
        :param app_name:
        :param doc_id:
        :param data:
        :param token:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        id = data.id
        doc = self.search_engine.get_doc(
            app_name=app_name,
            id=id
        )
        if not doc:
            return dict(
                error=dict(
                    code="ItemWasNotFound",
                    description=f"Item with id={id} was not found"
                )
            )
        else:
            return dict(
                content=doc.source.content
            )

    def raise_message(self, file_ext, data_info,app_name):
        if file_ext in  cyx.common.config.ext_office_file:
            self.broker.emit(
                app_name = app_name,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
                data= data_info
            )

        pass
