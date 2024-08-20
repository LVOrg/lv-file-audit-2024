import datetime
import typing
import uuid
import pymongo.errors
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
from cyx.repository import Repository

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
        super().__init__(request)
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
    def create_app(self,
               Name: str,
               Domain: str,
               Description: typing.Optional[str] = None,
               LoginUrl: str = None,
               ReturnUrlAfterSignIn: typing.Optional[str] = None,
               UserName: typing.Optional[str] = None,
               Password: typing.Optional[str] = None,
               ReturnSegmentKey: typing.Optional[str] = None,
               azure_app_name: typing.Optional[str] = None,
               azure_client_id: typing.Optional[str] = None,
               azure_tenant_id: typing.Optional[str] = None):
        docs = Repository.apps.app('admin')
        doc = docs.fields
        app_id = str(uuid.uuid4())
        secret_key = str(uuid.uuid4())
        docs.context.insert_one(
            doc.Id << app_id,
            doc.Name << Name,
            doc.ReturnUrlAfterSignIn << ReturnUrlAfterSignIn,
            doc.Domain << Domain,
            doc.LoginUrl << LoginUrl,
            doc.Description << Description,
            doc.Username << UserName,
            doc.Password << Password,
            doc.SecretKey << secret_key,
            doc.RegisteredOn << datetime.datetime.utcnow(),
            doc.ReturnSegmentKey << ReturnSegmentKey,
            doc.AppOnCloud.Azure.Name << azure_app_name,
            doc.AppOnCloud.Azure.ClientID << azure_client_id,
            doc.AppOnCloud.Azure.TenantID << azure_tenant_id

        )

        ret = cy_docs.DocumentObject(
            AppId=app_id,
            Name=Name,
            ReturnUrlAfterSignIn=ReturnUrlAfterSignIn,
            Domain=Domain,
            LoginUrl=LoginUrl,
            Description=Description,
            Username=UserName,
            SecretKey=secret_key,
            RegisteredOn=datetime.datetime.utcnow()
        )
        return ret

    def do_app_register(self, Data: AppInfoRegister) -> AppInfoRegisterResult:
        import cy_xdoc
        if not  hasattr(self.request,"username") or  getattr(self.request,"username") != "root":
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
            app = self.create_app(**save_data)
            ret.Data = app.to_pydantic()
            return ret
        except pymongo.errors.DuplicateKeyError as e:

            ret.Error = ErrorResult(
                Code= self.db_error_service.get_error_code(e),
                Fields=self.db_error_service.get_error_fields(e),
                Message=self.db_error_service.get_error_message(e)
            )
            return ret
        except Exception as e:
            ret.Error = ErrorResult(
                Code="System",
                Message="System error"
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

            ret.Error = ErrorResult(
                Code=cy_xdoc.get_error_code(e),
                Fields=cy_xdoc.get_error_fields(e),
                Message=cy_xdoc.get_error_message(e)
            )
            return ret
    def get_app_info(self, app_name, app_get: typing.Optional[str]):
        docs = Repository.apps.app(app_name)
        ret = docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields.Id,
            docs.fields.Name,
            docs.fields.Description,
            docs.fields.Domain,
            docs.fields.LoginUrl,
            docs.fields.ReturnUrlAfterSignIn,
            docs.fields.ReturnSegmentKey,
            cy_docs.fields.Apps >> docs.fields.AppOnCloud,
            docs.fields.SizeInGB

        ).match(docs.fields.NameLower == app_get.lower()).first_item()
        if ret is None:
            ret = docs.context.aggregate().project(
                cy_docs.fields.AppId >> docs.fields.Id,
                docs.fields.Name,
                docs.fields.Description,
                docs.fields.Domain,
                docs.fields.LoginUrl,
                docs.fields.ReturnUrlAfterSignIn,
                docs.fields.ReturnSegmentKey,
                cy_docs.fields.Apps >> docs.fields.AppOnCloud,
                docs.fields.AppOnCloud,
                docs.fields.SizeInGB

            ).match(docs.fields.Name == app_get).first_item()

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

        ret = self.get_app_info("admin", app_get=app_name)
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


        apps = Repository.apps.app(app_name).context.aggregate().project(
            cy_docs.fields.AppId >> Repository.files.fields.id,
            Repository.apps.fields.name,
            Repository.apps.fields.description,
            Repository.apps.fields.domain,
            Repository.apps.fields.login_url,
            Repository.apps.fields.return_url_afterSignIn,
            Repository.apps.fields.LatestAccess,
            Repository.apps.fields.AccessCount,
            Repository.apps.fields.RegisteredOn,
            cy_docs.fields.AzurePersonalAccountUrlLogin >> Repository.apps.fields.AppOnCloud.Azure.PersonalAccountUrlLogin,
            cy_docs.fields.AzureBusinessAccountUrlLogin >> Repository.apps.fields.AppOnCloud.Azure.BusinessAccountUrlLogin,
            Repository.apps.fields.AppOnCloud,
            Repository.apps.fields.SizeInGB

        ).sort(
            Repository.apps.fields.LatestAccess.desc(),
            Repository.apps.fields.Name.asc(),
            Repository.apps.fields.RegisteredOn.desc()
        )

        for app in apps:

            yield app.to_pydantic()
