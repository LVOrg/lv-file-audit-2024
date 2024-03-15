from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    Form,
    Query,
Path

)
from typing import Annotated
from cy_xdoc.auths import Authenticate
from cyx.common import config

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo


@controller.resource()
class SystemsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        self.request = request

    @controller.route.post(
        "/api/sys/admin/get_config", summary="Re run index search"
    )
    def get_config(self) -> dict:
        return config

