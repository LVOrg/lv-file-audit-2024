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
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
from cy_fucking_whore_microsoft.services.office_365_services import Office365Service
from cy_fucking_whore_microsoft.fucking_ms_wopi.fucking_wopi_services import FuckingWopiService
import cyx.common.basic_auth
from cy_fucking_whore_microsoft.fucking_ms_wopi.fucking_wopi_services import FuckingWopiService
from cy_fucking_whore_microsoft.services import (
    account_services, ondrive_services
)
@controller.resource()
class PagesController:
    # add class wide dependencies e.g. auth
    fucking_office_365_service = cy_kit.singleton(Office365Service)
    fucking_wopi_service = cy_kit.singleton(FuckingWopiService)
    fucking_azure_account_service: account_services.AccountService = cy_kit.singleton(account_services.AccountService)

    dependencies = [
        Depends(verify_auth)
    ]
    auth_service = cy_kit.singleton(cyx.common.basic_auth.BasicAuth)
    # you can define in the Controller init some FastApi Dependency and them are automatically loaded in controller methods
    def __init__(self,request: Request):
        self.request = request

    @controller.route.get(
        "/", summary="Home page"
    )
    def home_page(self):

        return cy_web.render_template(
            rel_path_to_template="index.html",
            render_data={"request": self.request, "app": get_meta_data()}
        )

    @controller.route.get(
        "/ms-action/{app_name}/{upload_id}", summary="Home page"
    )
    def ms_page(self, app_name: str, upload_id: str):
        from cy_fucking_whore_microsoft.ssl_utils.fucking_utils import generate_access_token
        from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
        editor = {

        }
        try:
            data_browser = self.fucking_wopi_service.get_action(doc_type="docx",action="view")
            access_token = self.fucking_azure_account_service.acquire_token(
                app_name=app_name
            )
            wopi_access_token_info = generate_access_token(
                issuer=cy_web.get_host_url(),
                audience=f"{cy_web.get_host_url()}/api/{app_name}/wopi/{upload_id}.docx",
                user="nttlong@lacviet.com.vn",
                docid=f"{upload_id}.docx",
                pfx_password="dxwopi"
            )

            access_token_ttl = ""
            # src = self.fucking_office_365_service.get_embed_iframe_url(app_name=app_name, upload_id=upload_id,
            #                                                            include_token=False)
            wopi_src = f"{cy_web.get_host_url()}/api/{app_name}/wopi/files/{upload_id}.docx"
            # wopi_src ='http://172.16.13.72:8012/lvfile/api/lv-docs/wopi/files/c638d1b1-a9de-4048-8619-8db2dcaabcd3?access_token=123'
            # wopi_src = f"http://172.16.13.72:8012/api/{app_name}/wopi/files/{upload_id}.{'docx'}"
            # wopi_src=f"https://1drv.ms/w/s!AhSDgZO1-y79glHQ1O0W0U3Wo14A?e=zU4kIT"
            # wopi_src = f"{cy_web.get_host_url()}/wopi/files/test.docx"
            # wopi_src = f"file:///C:/long/test.docx"
            # wopi_src="https://FFC-onenote.officeapps-df.live.com/hosting/GetWopiTestInfo.ashx"
            src = self.fucking_wopi_service.get_wopi_url_from_action(
                doc_type="docx",
                action="edit",
                wopi_src=wopi_src+"?access_token=123"
            )
            # src = self.fucking_wopi_service.get_wopi_url_from_action(
            #     doc_type="wopitest",
            #     action="view",
            #     wopi_src=wopi_src
            # )
            test_acc= str(uuid.uuid4())
            editor = dict(
                wopi_urlsrc = src,
                access_token_ttl =  wopi_access_token_info.access_token_ttl,
                access_token = wopi_access_token_info.access_token, #wopi_access_token_info.access_token,
                web_access_token = access_token
            )
            return cy_web.render_template(
                rel_path_to_template="office-editor.html",
                render_data={"request": self.request, "editor":editor}
            )
        except FuckingWhoreMSApiCallException as e:
            editor = dict(
                error= dict(
                    code=e.code,
                    message=e.message
                )
            )
            return cy_web.render_template(
                rel_path_to_template="office-editor.html",
                render_data={"request": self.request, "editor": editor}
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
            return Response(status_code=401)
        application,username = request_service.get_info(self.request)
        if application!="admin":
            await self.auth_service.check_request("admin", self.request)
        if username is None:
            await self.auth_service.check_request(application, self.request)

        """
        /home/vmadmin/python/cy-py/cy_controllers/pages/resource/html/login.html
        /home/vmadmin/python/cy-py/cy_controllers/pages/resource/html/index.html
        """
        res = cy_web.render_template("index.html", {"request": self.request, "app": get_meta_data()})
        token_service.set_cookie(res,token_service.generate_token(app=application,username=username))
        return res


