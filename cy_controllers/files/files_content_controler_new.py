from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,

)
from cy_controllers.common.base_controller import (
    BaseController
)

router = APIRouter()
controller = Controller(router)
version2=None
@controller.resource()
class FilesContentControllerNew(BaseController):

    @controller.router.get(
        "/api/{app_name}/file/{directory:path}" if version2 else "/api/{app_name}/file-new/{directory:path}" ,
        tags=["FILES-CONTENT"]
    )
    async def get_thumb(self, app_name: str, directory: str):
        return  await self.file_util_service.get_file_content_async(
            app_name=app_name,
            directory=directory,
            request=self.request
        )

    @controller.router.get(
        "/api/{app_name}/thumb/{directory:path}" if version2 else "/api/{app_name}/thumb-new/{directory:path}",
        tags=["FILES-CONTENT"]
    )
    async def get_thumb(self, app_name: str, directory: str):
        print("OK")