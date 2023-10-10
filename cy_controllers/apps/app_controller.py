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
class AppsController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]


    def __init__(self, request: Request):
        self.request = request

    @controller.route.post(
        "/api/apps/{app_name}/re_index", summary="Re run index search"
    )
    def re_index(self,app_name:str)->str:
        import cyx.common.msg
        self.msg_service.emit(
            app_name = app_name,
            message_type=cyx.common.msg.MSG_APP_RE_INDEX_ALL,
            data = dict(
                app_name = app_name,
                emit_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )

        )
        return app_name

    @controller.route.post("/api/admin/apps/register", summary="App register")
    def app_register(self, app: AppInfoRegisterModel) -> AppInfoRegisterResult:
        import cy_xdoc
        Data = app.Data
        if not self.request.username or self.request.username != "root":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED

            )
        ret = AppInfoRegisterResult()
        try:
            data = Data.dict()
            del data["AppId"]
            data["ReturnSegmentKey"] = Data.ReturnSegmentKey or "returnUrl"
            save_data = {
                k: v for k, v in data.items() if v is not None
            }
            if data.get("RegisteredOn"):
                del data["RegisteredOn"]
            app =  self.service_app.create(**save_data)
            ret.Data = app.to_pydantic()
            self.apps_cache.clear_cache()
            return ret
        except pymongo.errors.DuplicateKeyError as e:
            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret
        except Exception as e:
            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret

    @controller.route.post("/api/admin/apps/update/{app_name}", summary="update_app")
    def app_update(self,app_name: str, app: AppInfoRegisterModel) -> AppInfoRegisterResult:
        import cy_xdoc
        Data = app.Data
        if not self.request.username or self.request.username != "root":
            raise HTTPException(
                status_code= status.HTTP_401_UNAUTHORIZED

            )
        ret = AppInfoRegisterResult()
        try:
            data = Data.dict()
            del data["Name"]
            data["ReturnSegmentKey"] = Data.ReturnSegmentKey or "returnUrl"
            app = self.service_app.update(**data)
            ret.Data = app.to_pydantic()
            self.apps_cache.clear_cache()
            return ret
        except pymongo.errors.DuplicateKeyError as e:
            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret
        except Exception as e:
            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret

    @controller.route.post("/api/admin/apps/get/{get_app_name}")
    def get_info(self,get_app_name: str) -> AppInfo:
        """
        get application info if not exist return { AppId:null}
        lấy thông tin ứng dụng nếu không tồn tại return { AppId: null}
        :param get_app_name:
        :param token:
        :return:
        """
        app_name = "admin"
        ret = self.service_app.get_item(app_name, app_get=get_app_name)
        if ret:
            return ret.to_pydantic()
        else:
            return self.cy_docs.create_empty_pydantic(AppInfo)

    @controller.route.post("/api/admin/apps")
    def get_list_of_apps(self) -> typing.List[AppInfo]:
        """
        Get list of application. Every tenant has one application in file system
        Nhận danh sách ứng dụng. Mỗi đối tượng thuê có một ứng dụng trong hệ thống tệp
        :param token:
        :return:
        """
        app_name = "admin"
        for app in self.service_app.get_list(app_name):
            yield app.to_pydantic()