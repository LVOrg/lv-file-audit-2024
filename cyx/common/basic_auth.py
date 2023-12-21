from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.requests import Request
from fastapi.security.utils import get_authorization_scheme_param

import cy_kit
from cyx.common.jwt_utils import TokenVerifier
import secrets

# Add a basic HTTP authentication
security = HTTPBasic()
import cyx.common
import cyx.common.cacher
import jwt.exceptions
import cy_xdoc.services.apps
from user_agents import parse
class BasicAuth:
    def __init__(self,
                    token_verifier:TokenVerifier=cy_kit.singleton(TokenVerifier),
                    cacher: cyx.common.cacher.CacherService = cy_kit.singleton(cyx.common.cacher.CacherService),
                    app_services:cy_xdoc.services.apps.AppServices = cy_kit.singleton(cy_xdoc.services.apps.AppServices)
                ):
        self.token_verifier=token_verifier
        self.share_key = cyx.common.config.jwt.secret_key
        self.cacher = cacher
        self.app_services=app_services

    def raise_expr(self,ret_url:str=None, app_name:str=None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": 'Basic realm="simple"'})
        # if app_name is None:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        #                         detail="Invalid credentials",
        #                         headers={"WWW-Authenticate": 'Basic realm="simple"'})
        # else:
        #     app = self.app_services.get_item_with_cache(app_name)
        #     import cy_web
        #     login_url= cy_web.get_host_url()+"/login"
        #     location =login_url
        #     ret_key = app.ReturnSegmentKey or "ret"
        #     if app.LoginUrl is not  None and app.LoginUrl !="":
        #         login_url=app.LoginUrl
        #         if login_url[0:2]=='~/':
        #             login_url= cy_web.get_host_url()+"/"+login_url[2:]
        #     if app.ReturnUrlAfterSignIn and app.ReturnUrlAfterSignIn !="" and ret_url is None:
        #         import urllib.parse
        #         r_url = app.ReturnUrlAfterSignIn
        #         if r_url=='~/':
        #             r_url = cy_web.get_host_url()
        #         elif r_url[0:2]=='~/':
        #             r_url = cy_web.get_host_url()+"/"+r_url[2:]
        #         location = login_url+"?"+ret_key+"="+urllib.parse.quote(r_url.encode("utf-8"))
        #     else:
        #         import urllib.parse
        #         location = login_url + "?"+ret_key+"=" + urllib.parse.quote(ret_url.encode("utf-8"))
        #     raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
        #                         detail="Invalid credentials",
        #                         headers={"Location": location})

    def get_auth_bearer(self, request: Request):
        from cyx.token_manager.token_service import FILE_SERVICE_COOKIE_KEY
        try:
            if request.cookies and request.cookies.get('access_token_cookie'):
                return None, request.cookies.get('access_token_cookie')
            elif request.cookies and request.cookies.get(FILE_SERVICE_COOKIE_KEY):
                return None, request.cookies.get(FILE_SERVICE_COOKIE_KEY)
            elif request.headers.get("Authorization"):
                scheme, param = get_authorization_scheme_param(request.headers.get("Authorization"))
                return scheme, param
            else:
                return None,None

        except jwt.exceptions.DecodeError:
            return None, None

        except Exception as e:
            return None, None

    async def check_request(self,app_name:str, request: Request):
        from cy_xdoc.services.accounts import AccountService
        from fastapi.security import HTTPBasic, HTTPBasicCredentials

        if hasattr(request,"cookies") and isinstance(request.cookies,dict):
            token = request.cookies.get("cy-files-token")
            if token:
                token_infor = self.token_verifier.verify(share_key=self.share_key, token=token)
                if token_infor:
                    setattr(request, 'token_infor', token_infor)
                    return




        scheme, token = self.get_auth_bearer(request)

        if token and scheme=="Bearer":
            token_infor = self.token_verifier.verify(share_key=self.share_key,token=token)

            if token_infor:
                setattr(request,'token_infor',token_infor)
            else:
                self.raise_expr(ret_url=request.url._url, app_name=app_name)

        elif token and scheme=="Basic" :
            cr = await HTTPBasic()(request)
            check_app, check_user = tuple(cr.username.split('/'))
            check_password = cr.password
            acc_svc = cy_kit.singleton(AccountService)
            ok = acc_svc.validate(app_name=check_app,
                                  username=check_user,

                                  password=check_password)
            if ok:
                return
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect auth",
                    headers={"WWW-Authenticate": "Basic"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect auth",
                headers={"WWW-Authenticate": "Basic"},
            )
            # from cyx.token_manager.token_service import FILE_SERVICE_COOKIE_KEY
            # from cyx.token_manager.request_service import RequestService
            #
            # if request.headers.get('user-agent'):
            #
            #     user_agent = parse(request.headers.get('user-agent'))
            #     self.raise_expr(ret_url=request.url._url, app_name=app_name)





# def validate_credentials(credentials: HTTPBasicCredentials = Depends(security)):
#     # encode the credentials to compare
#     input_user_name = credentials.username.encode("utf-8")
#     input_password = credentials.password.encode("utf-8")
#
#     # DO NOT STORE passwords in plain text. Store them in secure location like vaults or database after encryption.
#     # This is just shown for educational purposes
#     stored_username = b'dinesh'
#     stored_password = b'dinesh'
#
#     is_username = secrets.compare_digest(input_user_name, stored_username)
#     is_password = secrets.compare_digest(input_password, stored_password)
#
#     if is_username and is_password:
#         return {"auth message": "authentication successful"}
#
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                         detail="Invalid credentials",
#                         headers={"WWW-Authenticate": "Basic"})
