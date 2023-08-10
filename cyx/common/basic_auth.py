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
        if app_name is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials",
                                headers={"WWW-Authenticate": 'Basic realm="simple"'})
        else:
            app = self.app_services.get_item_with_cache(app_name)
            import cy_web
            login_url= cy_web.get_host_url()+"/login"
            location =login_url
            ret_key = app.ReturnSegmentKey or "ret"
            if app.LoginUrl is not  None and app.LoginUrl !="":
                login_url=app.LoginUrl
                if login_url[0:2]=='~/':
                    login_url= cy_web.get_host_url()+"/"+login_url[2:]
            if app.ReturnUrlAfterSignIn and app.ReturnUrlAfterSignIn !="" and ret_url is None:
                import urllib.parse
                r_url = app.ReturnUrlAfterSignIn
                if r_url=='~/':
                    r_url = cy_web.get_host_url()
                elif r_url[0:2]=='~/':
                    r_url = cy_web.get_host_url()+"/"+r_url[2:]
                location = login_url+"?"+ret_key+"="+urllib.parse.quote(r_url.encode("utf-8"))
            else:
                import urllib.parse
                location = login_url + "?"+ret_key+"=" + urllib.parse.quote(ret_url.encode("utf-8"))
            raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                                detail="Invalid credentials",
                                headers={"Location": location})

    def get_auth_bearer(self, request: Request):
        try:
            authorization = request.headers.get("Authorization")
            if authorization:
                scheme, param = get_authorization_scheme_param(authorization)
                return scheme, param
            else:
                if request.cookies and request.cookies.get('access_token_cookie'):
                    return None,request.cookies.get('access_token_cookie')
                return None,None
        except jwt.exceptions.DecodeError:
            return None, None

        except Exception as e:
            return None, None

    def check_request(self,app_name:str, request: Request):
        scheme, token = self.get_auth_bearer(request)
        if token:
            token_infor = self.token_verifier.verify(share_key=self.share_key,token=token)
            if token_infor:
                setattr(request,'token_infor',token_infor)
            else:
                self.raise_expr(ret_url=request.url._url, app_name=app_name)
        else:
            if request.headers.get('user-agent'):
                from user_agents import parse
                user_agent = parse(request.headers.get('user-agent'))
                self.raise_expr(ret_url=request.url._url, app_name=app_name)




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
