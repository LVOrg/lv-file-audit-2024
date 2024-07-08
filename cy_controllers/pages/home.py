import uuid

import fastapi.responses
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
import os
from cy_xdoc.pages.meta_data import get_meta_data
import cy_web
from cyx.token_manager import (
    TokenService,RequestService
)
router = APIRouter()
controller = Controller(router)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from cy_xdoc.services.accounts import AccountService
from cy_xdoc.auths import Authenticate
import cy_kit
token_service= cy_kit.singleton(TokenService)
request_service = cy_kit.singleton(RequestService)
security = HTTPBasic()


def verify_auth(request:Request, credentials: HTTPBasicCredentials = Depends(security)):
    check_app, check_user  = token_service.get_info_from_token(request)
    if check_app and check_user:
        request_service.set_info(
            request=request, app_name=check_app, username=check_user
        )
        return True
    acc_svc = cy_kit.singleton(AccountService)
    username = credentials.username
    ok = False
    if '/' in username:
        check_app, check_user = tuple(username.split('/'))
        request_service.set_info(
            request=request,app_name = check_app, username= check_user
        )
        password = credentials.password

        ok = acc_svc.validate(app_name=check_app,
                              username=check_user,

                              password=password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect auth",
            headers={"WWW-Authenticate": "Negotiate, Basic realm=\"Lacviet Realm\""},
        )

    return credentials.username
import cyx.common.basic_auth
# from requests_kerberos import HTTPKerberosAuth
@controller.resource()
class PagesController:
    # add class wide dependencies e.g. auth


    dependencies = [
        Depends(verify_auth),

    ]
    auth_service = cy_kit.singleton(cyx.common.basic_auth.BasicAuth)
    # you can define in the Controller init some FastApi Dependency and them are automatically loaded in controller methods
    def __init__(self,request: Request):
        self.request = request

    @controller.route.get(
        "/", summary="Home page"
    )
    def home_page(self):
        from starlette.datastructures import URL
        app_data = get_meta_data(self.request)
        return cy_web.render_template(
            rel_path_to_template="index.html",
            render_data={"request": self.request, "app": app_data}
        )


    @controller.route.get(
        "{directory:path}", summary="Home page"
    )
    async def page_single(self, directory: str):
        from cyx.base import config
        directory = directory.split('?')[0]
        check_dir_path = os.path.abspath(os.path.join(
            cy_web.get_static_dir(),
            "views",
            directory.lstrip('/').rstrip('/').replace('/', os.sep)
        ))

        if not os.path.exists(check_dir_path):
            return Response(status_code=404)
        application,username = request_service.get_info(self.request)
        if application!="admin":
            await self.auth_service.check_request("admin", self.request)
        if username is None:
            await self.auth_service.check_request(application, self.request)

        """
        /home/vmadmin/python/cy-py/cy_controllers/pages/resource/html/login.html
        /home/vmadmin/python/cy-py/cy_controllers/pages/resource/html/index.html
        """
        app_data = get_meta_data(self.request)
        app_data["version"]=os.getenv("PRODUCTION_BUILT_ON") or "dev"
        res = cy_web.render_template("index.html",
                                     {
                                         "request": self.request, "app": app_data,
                                         "version": os.getenv("PRODUCTION_BUILT_ON") or "dev"
                                        }
                                     )
        token_service.set_cookie(res,token_service.generate_token(app=application,username=username))
        return res


