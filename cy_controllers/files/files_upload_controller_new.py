
from cyx.common import config
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,

    UploadFile,
    Form, File
)

from cy_xdoc.auths import Authenticate

import datetime

from typing import Annotated
from fastapi.requests import Request


router = APIRouter()
controller = Controller(router)

from cy_controllers.common.base_controller import BaseController


async def get_main_file_id_async(fs):
    st = datetime.datetime.utcnow()
    ret = await fs.get_id_async()
    n = (datetime.datetime.utcnow() - st).total_seconds()
    print(f"get_main_file_id_async={n}")
    return ret


version2 = config.generation if hasattr(config, "generation") else None

from concurrent.futures import ThreadPoolExecutor




@controller.resource()
class FilesUploadControllerNew(BaseController):
    dependencies = [
        Depends(Authenticate),
        # Depends(ThreadPoolContainer.executor)

    ]

    def __init__(self, request: Request,):

        super().__init__(request)
        self.pool = None


    @controller.route.post(
        "/api/{app_name}/files/upload" if version2 else "/api/{app_name}/files/upload_new", summary="Upload file",
        tags=["FILES"]
    )
    async def upload_async(self,
                           app_name: str,
                           UploadId: Annotated[str, Form()],
                           Index: Annotated[int, Form()],
                           FilePart: Annotated[UploadFile, File()]):
        upload = self.file_util_service.get_upload(app_name=app_name, upload_id=UploadId)
        if upload.get("error"):
            return dict(
                Error=dict(
                    Code="System",
                    Message=upload["error"]
                )
            )

        ret = await self.file_util_service.save_file_async(
            app_name=app_name,
            content=FilePart,
            upload=upload,
            index=Index,
            pool=self.pool
        )
        return ret
