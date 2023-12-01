import datetime
import typing
import uuid

import cy_docs
import cy_kit
import cy_web
from cyx.common.base import DbConnect
from cy_xdoc.models.apps import App
import cyx.common
import cyx.common.cacher
from cyx.cache_service.memcache_service import MemcacheServices
from cy_azure.services.ms_apps_services import MSAppService

class AppsCacheService:
    def __init__(self,
                 cacher=cy_kit.singleton(MemcacheServices)):
        self.cacher = cacher
        self.cache_key = "APP:CACHE"


    def clear_cache(self):
        self.cacher.delete_key(self.cache_key)


class AppServices:

    def __init__(self,
                 db_connect=cy_kit.singleton(cyx.common.base.DbConnect),
                 cacher=cy_kit.singleton(cyx.common.cacher.CacherService),
                 ms_app=cy_kit.singleton(MSAppService)
                 ):
        self.db_connect = db_connect
        self.config = cyx.common.config
        self.admin_db = self.config.admin_db_name
        self.cacher = cacher
        self.cache_type = f"{App.__module__}.{App.__name__}"
        self.ms_app = ms_app

    def get_list(self, app_name: str):
        docs = self.db_connect.db(app_name).doc(App)

        ret = docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields._id,
            docs.fields.name,
            docs.fields.description,
            docs.fields.domain,
            docs.fields.login_url,
            docs.fields.return_url_afterSignIn,
            docs.fields.LatestAccess,
            docs.fields.AccessCount,
            docs.fields.RegisteredOn,
            cy_docs.fields.AzureLoginUrl>>docs.fields.AppOnCloud.Azure.UrlLogin

        ).sort(
            docs.fields.LatestAccess.desc(),
            docs.fields.Name.asc(),
            docs.fields.RegisteredOn.desc()
        )
        return ret

    def get_item(self, app_name, app_get:typing.Optional[str]):
        docs = self.db_connect.db(app_name).doc(App)
        ret = docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields.Id,
            docs.fields.Name,
            docs.fields.Description,
            docs.fields.Domain,
            docs.fields.LoginUrl,
            docs.fields.ReturnUrlAfterSignIn,
            docs.fields.ReturnSegmentKey,
            cy_docs.fields.Apps>>docs.fields.AppOnCloud

        ).match(docs.fields.NameLower == app_get.lower()).first_item()
        if ret is None:
            ret = docs.context.aggregate().project(
                cy_docs.fields.AppId >> docs.fields.Id,
                docs.fields.Name,
                docs.fields.Description,
                docs.fields.Domain,
                docs.fields.LoginUrl,
                docs.fields.ReturnUrlAfterSignIn,
                docs.fields.ReturnSegmentKey,
                cy_docs.fields.Apps >> docs.fields.AppOnCloud

            ).match(docs.fields.Name == app_get).first_item()

        return ret

    def get_item_with_cache(self, app_name):
        ret = self.cacher.get_by_key(self.cache_type, app_name)
        if ret:
            return ret
        else:
            ret = self.get_item(app_name='admin', app_get=app_name)
            self.cacher.add_to_cache(self.cache_type, app_name, ret)
            return ret

    def create(self,
               Name: str,
               Domain: str,
               Description: typing.Optional[str] = None,
               LoginUrl: str = None,
               ReturnUrlAfterSignIn: typing.Optional[str] = None,
               UserName: typing.Optional[str] = None,
               Password: typing.Optional[str] = None,
               ReturnSegmentKey: typing.Optional[str] = None,
               azure_app_name: typing.Optional[str] = None,
               azure_client_id: typing.Optional[str] = None,
               azure_tenant_id: typing.Optional[str] = None):
        docs = self.db_connect.db('admin').doc(App)
        doc = docs.fields
        app_id = str(uuid.uuid4())
        secret_key = str(uuid.uuid4())
        docs.context.insert_one(
            doc.Id << app_id,
            doc.Name << Name,
            doc.ReturnUrlAfterSignIn << ReturnUrlAfterSignIn,
            doc.Domain << Domain,
            doc.LoginUrl << LoginUrl,
            doc.Description << Description,
            doc.Username << UserName,
            doc.Password << Password,
            doc.SecretKey << secret_key,
            doc.RegisteredOn << datetime.datetime.utcnow(),
            doc.ReturnSegmentKey << ReturnSegmentKey,
            doc.AppOnCloud.Azure.Name << azure_app_name,
            doc.AppOnCloud.Azure.ClientID << azure_client_id,
            doc.AppOnCloud.Azure.TenantID << azure_tenant_id

        )

        ret = cy_docs.DocumentObject(
            AppId=app_id,
            Name=Name,
            ReturnUrlAfterSignIn=ReturnUrlAfterSignIn,
            Domain=Domain,
            LoginUrl=LoginUrl,
            Description=Description,
            Username=UserName,
            SecretKey=secret_key,
            RegisteredOn=datetime.datetime.utcnow()
        )
        return ret
    def save_azure_access_token(self,
                                app_name:str,
                                azure_access_token:str,
                                azure_refresh_token:str,
                                azure_token_id:str):
        docs = self.db_connect.db('admin').doc(App)
        doc = docs.fields
        ret = docs.context.update(
            doc.Name == app_name,
            doc.AppOnCloud.Azure.AccessToken << azure_access_token,
            doc.AppOnCloud.Azure.RefreshToken << azure_refresh_token,
            doc.AppOnCloud.Azure.TokenId<<azure_token_id

        )
        return ret
    def update(self,
               Name: str,
               Description: typing.Optional[str] = None,
               azure_app_name: typing.Optional[str] = None,
               azure_client_id: typing.Optional[str] = None,
               azure_tenant_id: typing.Optional[str] = None,
               azure_client_secret:typing.Optional[str]=None,
               azure_client_is_personal_acc: typing.Optional[bool]=False):
        docs = self.db_connect.db('admin').doc(App)
        doc = docs.fields
        url_azure_login = None
        if isinstance(azure_client_id,str):
            from cy_azure.fwcking_auth import scopes, urls_auth
            redirect_url= f"{cy_web.get_host_url()}/api/{Name}/azure/after_login"
            if azure_client_is_personal_acc:
                url_azure_login = urls_auth.get_personal_account_login_url(
                    client_id = azure_client_id,
                    scopes = scopes.get_one_drive(),
                    redirect_uri = redirect_url
                )
            else:
                url_azure_login = urls_auth.get_business_account_login_url(
                    client_id=azure_client_id,
                    tenant_id= azure_tenant_id,
                    scopes=scopes.get_one_drive(),
                    redirect_uri=redirect_url
                )




            # url_azure_login = self.ms_app.get_login_url(
            #     client_id=azure_client_id,
            #     redirect_uri= f"{cy_web.get_host_url()}/api/{Name}/azure/after_login"
            # )
            # url_azure_login+=f"?lv-file-app-name={Name}"
        ret = docs.context.update(
            doc.Name == Name,
            doc.Description << Description,
            doc.ModifiedOn << datetime.datetime.utcnow(),
            doc.AppOnCloud.Azure.Name << azure_app_name,
            doc.AppOnCloud.Azure.ClientId << azure_client_id,
            doc.AppOnCloud.Azure.TenantId << azure_tenant_id,
            doc.AppOnCloud.Azure.UrlLogin << url_azure_login,
            doc.AppOnCloud.Azure.ClientSecret << azure_client_secret,
            doc.AppOnCloud.Azure.IsPersonal << azure_client_is_personal_acc,
            doc.NameLower<<Name.lower()

        )
        agg = docs.context.aggregate().project(
            cy_docs.fields.AppId >> docs.fields.Id,
            docs.fields.Name,
            docs.fields.Description,
            docs.fields.Domain,
            docs.fields.LoginUrl,
            docs.fields.ReturnUrlAfterSignIn,
            docs.fields.ReturnSegmentKey,
            cy_docs.fields.Apps >> docs.fields.AppOnCloud

        )
        ret_app = agg.match((doc.NameLower == Name.lower())|(doc.Name == Name)).first_item()
        # if ret_app is None:
        #     ret_app = agg.match(docs.fields.Name == Name).first_item()
        return ret_app

    def create_default_app(self, domain: str, login_url: str, return_url_after_sign_in: str):
        document = self.db_connect.db('admin').doc(App)
        default_amdin_db = self.admin_db
        application = document.context @ (document.fields.Name == default_amdin_db)
        if application is None:
            document.context.insert_one(
                document.fields.Name << default_amdin_db,
                document.fields.Domain << domain,
                document.fields.RegisteredOn << datetime.datetime.utcnow(),
                document.fields.LoginUrl << login_url,
                document.fields.ReturnUrlAfterSignIn << return_url_after_sign_in
            )


