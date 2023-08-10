import typing

import pydantic

import cy_docs
import cy_kit
import cy_web
from cy_xdoc.auths import Authenticate
import fastapi.params
from cy_xdoc.services.apps import AppServices
from cy_xdoc.controllers.models.apps import AppInfo


@cy_web.hanlder(method="post", path="admin/apps/get/{get_app_name}")
def get_application_info(get_app_name: str, token=fastapi.Depends(Authenticate)) -> AppInfo:
    """
    get application info if not exist return { AppId:null}
    lấy thông tin ứng dụng nếu không tồn tại return { AppId: null}
    :param get_app_name:
    :param token:
    :return:
    """
    app_name="admin"
    app_service = cy_kit.single(AppServices)
    ret = app_service.get_item(app_name, app_get=get_app_name)
    if ret:
        return ret.to_pydantic()
    else:
        return cy_docs.create_empty_pydantic(AppInfo)

