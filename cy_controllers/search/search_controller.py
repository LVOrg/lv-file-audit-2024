import datetime
import typing

from cy_controllers.models.apps import(
        AppInfo,
        AppInfoRegister,
        AppInfoRegisterResult,
        ErrorResult, AppInfoRegisterModel
    )
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response
)
from cy_xdoc.auths import Authenticate

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo
@controller.resource()
class SearchController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.get("/api/{app_name}/content/update_by_conditional")
    def file_content_update_by_conditional(
            self,
            app_name: str,
            conditional:typing.Optional[dict],
            data_update: typing.Optional[dict]):
        """
        Update data to search engine with conditional<br/>
        Cập nhật dữ liệu lên công cụ tìm kiếm có điều kiện
        :param app_name:
        :param doc_id:
        :param data:
        :param token:
        :return:
        """
        ret = self.search_engine.update_by_conditional(
            app_name=app_name,
            conditional=conditional,
            data=data_update
        )
        return ret
