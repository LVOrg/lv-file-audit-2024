import cy_web
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
import cy_xdoc.services.accounts
import cy_kit

__is_the_first_time__ = None

import cy_xdoc.services.apps


# def validate_account(request: Request, username: str, password: str) -> bool:
#     global __is_the_first_time__
#     account_service = cy_kit.inject(cy_xdoc.services.accounts.AccountService)
#     app_service = cy_kit.inject(cy_xdoc.services.apps.AppServices)
#     if __is_the_first_time__ is None:
#         app_service.create_default_app(
#             login_url=cy_web.get_host_url() + "/login",
#             domain=cy_web.get_host_url(),
#             return_url_after_sign_in=cy_web.get_host_url()
#         )
#         account_service.create_default_user()
#     __is_the_first_time__ = True
#     app_name = username.split('/')[0]
#     username = username.split('/')[1]
#     if account_service.validate(app_name, username, password):
#         return dict(
#             application=app_name,
#             username=username,
#             is_ok=True
#         )
#     else:
#         return dict(
#             application=app_name,
#             username=username,
#             is_ok=False
#         )
from typing import Optional, Dict

@cy_web.auth_type(OAuth2PasswordBearer)
class Authenticate:
    def validate(self,
                 request: Request,
                 username: str,
                 application: str, apps=cy_kit.inject(cy_xdoc.services.apps.AppServices)) -> bool:

        return True

    def validate_account(self,request: Request, username: str, password: str) -> bool:
        global __is_the_first_time__
        account_service = cy_kit.inject(cy_xdoc.services.accounts.AccountService)
        app_service = cy_kit.inject(cy_xdoc.services.apps.AppServices)
        if __is_the_first_time__ is None:
            app_service.create_default_app(
                login_url=cy_web.get_host_url() + "/login",
                domain=cy_web.get_host_url(),
                return_url_after_sign_in=cy_web.get_host_url()
            )
            account_service.create_default_user()
        __is_the_first_time__ = True
        app_name = username.split('/')[0]
        username = username.split('/')[1]
        if account_service.validate(app_name, username, password):
            return dict(
                application=app_name,
                username=username,
                is_ok=True
            )
        else:
            return dict(
                application=app_name,
                username=username,
                is_ok=False
            )