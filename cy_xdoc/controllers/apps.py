import cy_kit
import cy_web
from cy_xdoc.auths import Authenticate
import fastapi.params
from typing import List
from cy_xdoc.services.apps import AppServices
from cy_xdoc.controllers.models.apps import AppInfo
@cy_web.hanlder(method="post", path="admin/apps")
def get_list_of_apps(token = fastapi.Depends(Authenticate))->List[AppInfo]:
    """
    Get list of application. Every tenant has one application in file system
    Nhận danh sách ứng dụng. Mỗi đối tượng thuê có một ứng dụng trong hệ thống tệp
    :param token:
    :return:
    """
    app_name="admin"
    app_service=cy_kit.single(AppServices)
    for app in  app_service.get_list(app_name):
        yield app.to_pydantic()

