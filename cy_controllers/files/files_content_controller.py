from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response

)
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse,mimetypes
)
router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
@controller.resource()
class FilesContentController(BaseController):

    def __init__(self,request:Request):
        self.request = request
    @controller.route.get(
        "/api/{app_name}/files/test", summary="Upload file"
    )
    async def test(self,app_name:str)->str:
        self.logger_service.info(app_name)

        return  "OK"
    @controller.router.get(
        "/api/{app_name}/thumb/{directory:path}"
    )
    async def get_thumb_of_files_async(self,app_name: str, directory: str):
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