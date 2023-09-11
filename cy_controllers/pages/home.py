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
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@controller.resource()
class PagesController:
    # add class wide dependencies e.g. auth
    dependencies = [
        Depends(verify_auth)
    ]

    # you can define in the Controller init some FastApi Dependency and them are automatically loaded in controller methods
    def __init__(self,request: Request):
        pass

    @controller.route.get(
        "/", summary="Home page"
    )
    def home_page(self, request: Request):
        return cy_web.render_template(
            rel_path_to_template="index.html",
            render_data={"request": request, "app": get_meta_data()}
        )

    @controller.route.get(
        "{directory:path}", summary="Home page"
    )
    async def page_single(self, directory: str, request: Request):
        directory = directory.split('?')[0]
        check_dir_path = os.path.abspath(os.path.join(
            cy_web.get_static_dir(),
            "views",
            directory.lstrip('/').rstrip('/').replace('/', os.sep)
        ))

        if not os.path.exists(check_dir_path):
            return Response(status_code=401)
        application,username = request_service.get_info(request)
        res = cy_web.render_template("index.html", {"request": request, "app": get_meta_data()})
        res.set_cookie("token",token_service.generate_token(app=application,username=username))
        return res
