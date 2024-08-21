import cy_web
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
import cy_xdoc.services.accounts
import cy_kit

__is_the_first_time__ = None

import cy_xdoc.services.apps

from cyx.cache_service.memcache_service import MemcacheServices
from cyx.repository import Repository
from datetime import datetime

from cyx.common import config


@cy_web.auth_type(OAuth2PasswordBearer)
class Authenticate:
    def validate(self,
                 request: Request,
                 username: str,
                 application: str, apps=None) -> bool:

        return True
    def create_default_app(self, domain: str, login_url: str, return_url_after_sign_in: str):
        document = Repository.apps.app('admin')
        application = document.context @ (document.fields.Name == config.admin_db_name)
        if application is None:
            document.context.insert_one(
                document.fields.Name << config.admin_db_name,
                document.fields.Domain << domain,
                document.fields.RegisteredOn << datetime.utcnow(),
                document.fields.LoginUrl << login_url,
                document.fields.ReturnUrlAfterSignIn << return_url_after_sign_in
            )
    def validate_account(self, request: Request, username: str, password: str) -> dict:
        global __is_the_first_time__
        account_service = cy_kit.singleton(cy_xdoc.services.accounts.AccountService)
        # app_service = cy_kit.singleton(cy_xdoc.services.apps.AppServices)
        cache_service = cy_kit.singleton(MemcacheServices)
        key = f"validate_account/{username}/{password}"
        cache_value = cache_service.get_dict(key)
        if isinstance(cache_value, dict):
            return cache_value
        if __is_the_first_time__ is None:
            self.create_default_app(
                login_url=cy_web.get_host_url(request) + "/login",
                domain=cy_web.get_host_url(request),
                return_url_after_sign_in=cy_web.get_host_url(request)
            )
            account_service.create_default_user()
        __is_the_first_time__ = True
        app_name = username.split('/')[0]
        username = username.split('/')[1]
        if account_service.validate(app_name, username, password):
            ret = dict(
                application=app_name,
                username=username,
                is_ok=True
            )
            cache_service.set_dict(key,ret,expiration=60*60*4)
            setattr(request,"username",username)
            setattr(request, "password", password)
            setattr(request, "application", app_name)
            return ret
        else:
            return dict(
                application=app_name,
                username=username,
                is_ok=False
            )
