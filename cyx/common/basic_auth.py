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
from cyx.local_api_services import LocalAPIService
class BasicAuth:
    def __init__(self,
                    token_verifier:TokenVerifier=cy_kit.singleton(TokenVerifier),
                    cacher: cyx.common.cacher.CacherService = cy_kit.singleton(cyx.common.cacher.CacherService),
                    local_app_service:LocalAPIService = cy_kit.singleton(LocalAPIService)

                ):
        self.token_verifier=token_verifier
        self.share_key = cyx.common.config.jwt.secret_key
        self.cacher = cacher
        self.local_app_service = local_app_service

    def raise_expr(self,ret_url:str=None, app_name:str=None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": 'Basic realm="simple"'})
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
        if request.method in ["GET","POST","PUT","DELETE"]:
            token =  request.query_params.get("token")
            if token:
                token_infor = self.token_verifier.verify(share_key=self.share_key, token=token)
                if token_infor:
                    setattr(request, 'token_infor', token_infor)
                    return
        if hasattr(request,"cookies") and isinstance(request.cookies,dict):
            token = request.cookies.get("cy-files-token")
            if token:
                token_infor = self.token_verifier.verify(share_key=self.share_key, token=token)
                if token_infor:
                    setattr(request, 'token_infor', token_infor)
                    return

        if request.query_params.get("local-share-id") and request.query_params.get("app-name"):
            if self.local_app_service.check_local_share_id(
                app_name = request.query_params.get("app-name"),
                local_share_id= request.query_params.get("local-share-id")

            ):
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
                    headers={"WWW-Authenticate": 'Basic'},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect auth",
                headers={"WWW-Authenticate":  'Basic'},
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
