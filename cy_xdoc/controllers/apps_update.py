import pymongo

import cy_kit
import cy_web
from cy_xdoc.auths import Authenticate
import fastapi.params
from cy_xdoc.services.apps import AppServices
from cy_xdoc.controllers.models.apps import AppInfo, AppInfoRegister, AppInfoRegisterResult,ErrorResult
import cy_xdoc
from cy_xdoc.controllers import  apps as apps_cache
@cy_web.hanlder(method="post", path="admin/apps/update/{app_name}")
def get_list_of_apps(app_name:str, request:fastapi.Request,Data: AppInfoRegister,
                     token=fastapi.Depends(Authenticate)) -> AppInfoRegisterResult:
    if not request.username or request.username!="root":
        raise fastapi.exceptions.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED

        )
    ret = AppInfoRegisterResult()
    try:
        data = Data.dict()
        del data["Name"]
        data["ReturnSegmentKey"] = Data.ReturnSegmentKey or "returnUrl"
        app = cy_xdoc.container.service_app.update(**data)
        ret.Data = app.to_pydantic()
        apps_cache.clear_cache()
        return ret
    except pymongo.errors.DuplicateKeyError as e:
        ret.Error = ErrorResult(
            Code= cy_xdoc.get_error_code(e),
            Fields = cy_xdoc.get_error_fields(e),
            Message = cy_xdoc.get_error_message(e)
        )
        return ret
    except Exception as e:
        ret.Error = ErrorResult(
            Code=cy_xdoc.get_error_code(e),
            Fields=cy_xdoc.get_error_fields(e),
            Message=cy_xdoc.get_error_message(e)
        )
        return ret


