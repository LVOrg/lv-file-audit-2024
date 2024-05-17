import datetime
import typing
import cy_docs
from cy_controllers.models.apps import (
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
    Response, Body
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
        "/api/apps/{app_name}/re_index", summary="Re run index search",
        tags=["APPS"]


    )
    def re_index(self, app_name: str) -> str:
        import cyx.common.msg
        self.msg_service.emit(
            app_name=app_name,
            message_type=cyx.common.msg.MSG_APP_RE_INDEX_ALL,
            data=dict(
                app_name=app_name,
                emit_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )

        )
        return app_name


    def do_app_register(self, Data: AppInfoRegister) -> AppInfoRegisterResult:
        import cy_xdoc
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
            app = self.service_app.create(**save_data)
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

    @controller.route.post("/api/admin/apps/register", summary="App register",
        tags=["APPS"])
    def app_register(self, Data: AppInfoRegister=Body(embed=True)) -> AppInfoRegisterResult:
        return self.do_app_register(Data)

    @controller.route.post("/api/apps/admin/register", summary="App register",
        tags=["APPS"])
    def app_register(self, Data: AppInfoRegister = Body(embed=True)) -> AppInfoRegisterResult:
        return self.do_app_register(Data)
    @controller.route.post("/api/admin/apps/update/{app_name}", summary="update_app",
        tags=["APPS"])
    def app_update(self, app_name: str, Data: AppInfoRegister=Body(embed=True)) -> AppInfoRegisterResult:

        import cy_xdoc

        if not self.request.username or self.request.username != "root":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED

            )

        try:
            app = self.service_app.update(
                request = self.request,
                Name=Data.Name,
                Description=Data.Description,
                azure_app_name=Data.AppOnCloud.Azure.Name if Data.AppOnCloud and Data.AppOnCloud.Azure and Data.AppOnCloud.Azure.Name else None,
                azure_client_id=Data.AppOnCloud.Azure.ClientId if Data.AppOnCloud and Data.AppOnCloud.Azure and Data.AppOnCloud.Azure.ClientId else None,
                azure_tenant_id=Data.AppOnCloud.Azure.TenantId if Data.AppOnCloud and Data.AppOnCloud.Azure and Data.AppOnCloud.Azure.TenantId else None,
                azure_client_secret=Data.AppOnCloud.Azure.ClientSecret if Data.AppOnCloud and Data.AppOnCloud.Azure and Data.AppOnCloud.Azure.ClientSecret else None,
                azure_client_is_personal_acc=Data.AppOnCloud.Azure.IsPersonal if Data.AppOnCloud and Data.AppOnCloud.Azure and Data.AppOnCloud.Azure.IsPersonal else False

            )
            ret = AppInfoRegisterResult()
            data = Data.dict()

            data["ReturnSegmentKey"] = Data.ReturnSegmentKey or "returnUrl"

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
            raise e
            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret

    @controller.route.post("/api/admin/apps/get/{app_name}",
        tags=["APPS"])
    def get_info(self, app_name: str) -> AppInfo:
        """
        get application info if not exist return { AppId:null}
        lấy thông tin ứng dụng nếu không tồn tại return { AppId: null}
        :param get_app_name:
        :param token:
        :return:
        """

        ret = self.service_app.get_item("admin", app_get=app_name)
        if ret:
            return ret.to_pydantic()
        else:
            return cy_docs.create_empty_pydantic(AppInfo)

    @controller.route.post("/api/admin/apps",
        tags=["APPS"])
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
