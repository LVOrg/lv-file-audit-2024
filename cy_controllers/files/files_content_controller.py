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
    Form, File
)

from cy_controllers.common.base_controller import BaseController, Authenticate
router = APIRouter()
controller = Controller(router)
@controller.resource()
class FilesContentController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    def __init__(self, request: Request):
        super().__init__(request)

    @controller.route.post(
        "/api/{app_name}/files/test", summary="Upload file"
    )
    async def test(self,app_name:str)->str:
        self.logger_service.info(app_name)

        return  "OK"