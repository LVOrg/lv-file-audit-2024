"""
This is a controller for all content of resource has been upload before.
Including: Content raw content, thumb image of any file with specific file extension
"""

import os
import pathlib
import traceback


import requests.exceptions
from fastapi import (
    APIRouter,
    Response,
    Body

)

from fastapi_router_controller import Controller

import bson
import cy_web
import cyx.common.msg
from cy_controllers.common.base_controller import (
    BaseController
)
from cy_controllers.models.file_contents import (
    ReadableParam
)
from cyx.repository import Repository

router = APIRouter()
controller = Controller(router)
version2=None
@controller.resource()
class FilesContentController(BaseController):
    """
    File content controller
    """

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



        file_path = await self.thumb_service.get_async(app_name,directory,700)
        if file_path is not None:
            ret = await cy_web.cy_web_x.streaming_async(file_path, self.request, "image/webp")
            return ret
        return Response(
                    status_code=404, content="Resource was not found"
                )



    def get_full_path_of_local_from_cache(self, upload)->str:
        """
        get physical path of an upload
        @param upload:
        @return:
        """

        key = f"{self.config.file_storage_path}/{__file__}/{type(self).__name__}/get_full_path_of_local_from_cache/{upload.id}"
        ret = self.memcache_service.get_str(key)
        if ret is not None:
            return ret
        main_file_id = ""
        if hasattr(upload,"MainFileId") and isinstance(upload.MainFileId,str):
            main_file_id = upload.MainFileId
        if isinstance(upload,dict):
            main_file_id = upload.get(Repository.files.fields.MainFileId.__name__)
        if "://" not in main_file_id:
            raise FileNotFoundError()
        full_path: str= str(os.path.join(self.config.file_storage_path,main_file_id[len("local://"):]))
        full_path = os.path.join(str(pathlib.Path(full_path).parent.parent), upload.FullFileNameLower)
        if not os.path.isfile(full_path):
            raise FileNotFoundError()
        self.memcache_service.set_str(key, full_path)
        ret = full_path
        return ret

    @controller.router.get(
        "/api/{app_name}/file/{directory:path}" ,
        tags=["FILES-CONTENT"]
    )
    async def get_content_from_all(self, app_name: str, directory: str):

        """
        Get or download content from server file. For download type url?download
        @param app_name:
        @param directory:
        @return:
        """

        if len(directory.split('/'))>2:
            directory = directory.split('/')[0]+"/"+directory.split('/')[1]
        try:
            return await self.file_util_service.get_file_content_async(request=self.request,app_name=app_name,directory=directory)
        except requests.exceptions.HTTPError as ex:
            return Response(content=traceback.format_exc(),status_code=ex.response.status_code)
        except FileNotFoundError:
            return Response(content="Content was not found", status_code=404)

    @controller.router.get("/api/{app_name}/thumbs/{directory:path}" ,tags=["FILES-CONTENT"])
    async def get_thumb_of_files(self, app_name: str, directory: str):
        """
        Xem hoặc tải nội dung file
        :param app_name:
        :return:
        @param app_name:
        @param directory:
        """

        if not directory.split('/')[-1].split('.')[0].isnumeric():
            raise ValueError(f"{directory} must be end with number")
        size= int(directory.split('/')[-1].split('.')[0])
        file_path = await self.thumb_service.get_async(app_name, directory, size)
        if file_path is None:
            return Response(
                status_code=404
            )
        if isinstance(file_path,bson.ObjectId):
            fs= self.file_util_service.get_fs_mongo(app_name,file_id=file_path)
            ret = await cy_web.cy_web_x.streaming_async(fs, self.request, "image/webp")
            return ret

        if file_path is not None and os.stat(file_path).st_size>0:

            ret = await cy_web.cy_web_x.streaming_async(file_path, self.request, "image/webp")
            return ret
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
        :param data:
        :return:
        """

        upload_id: str|None = data.id
        doc = self.search_engine.get_doc(
            app_name=app_name,
            id=upload_id
        )
        if not doc:
            return dict(
                Error=dict(
                    Code="ItemWasNotFound",
                    Message=f"Item with id={id} was not found"
                )
            )
        return dict(
            content=doc.source.content_vn
        )

    def raise_message(self, file_ext, data_info,app_name):
        """
        Send to RabbitMQ a message that tell another pod one file have been uploaded
        @param file_ext:
        @param data_info:
        @param app_name:
        @return:
        """
        if file_ext in  cyx.common.config.ext_office_file:
            self.broker.emit(
                app_name = app_name,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
                data= data_info
            )




