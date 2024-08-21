# import datetime
# import typing
# import uuid
#
# import cy_docs
# import cy_kit
# import cy_web
# from cyx.common.base import DbConnect
# import cyx.common
# import cyx.common.cacher
# from cyx.cache_service.memcache_service import MemcacheServices
#
#
#
#
# class AppsCacheService:
#     def __init__(self,
#                  cacher=cy_kit.singleton(MemcacheServices)):
#         self.cacher = cacher
#         self.cache_key = "APP:CACHE"
#
#     def clear_cache(self):
#         self.cacher.delete_key(self.cache_key)
#
#
# from cyx.common.base import DbCollection
#
# from cyx.cache_service.memcache_service import MemcacheServices
# class AppServices:
#
#     def __init__(self,
#                  db_connect=cy_kit.singleton(cyx.common.base.DbConnect),
#                  memcache_service=cy_kit.singleton(MemcacheServices),
#
#                  ):
#         self.db_connect = db_connect
#         self.config = cyx.common.config
#         self.admin_db = self.config.admin_db_name
#         self.memcache_service = memcache_service
#
#     def get_queryable(self) -> DbCollection[App]:
#         return self.db_connect.db("admin").doc(App)
#
#     def get_list(self, app_name: str):
#         docs = self.db_connect.db(app_name).doc(App)
#
#         ret = docs.context.aggregate().project(
#             cy_docs.fields.AppId >> docs.fields._id,
#             docs.fields.name,
#             docs.fields.description,
#             docs.fields.domain,
#             docs.fields.login_url,
#             docs.fields.return_url_afterSignIn,
#             docs.fields.LatestAccess,
#             docs.fields.AccessCount,
#             docs.fields.RegisteredOn,
#             cy_docs.fields.AzurePersonalAccountUrlLogin >> docs.fields.AppOnCloud.Azure.PersonalAccountUrlLogin,
#             cy_docs.fields.AzureBusinessAccountUrlLogin >> docs.fields.AppOnCloud.Azure.BusinessAccountUrlLogin,
#             docs.fields.AppOnCloud,
#             docs.fields.SizeInGB
#
#         ).sort(
#             docs.fields.LatestAccess.desc(),
#             docs.fields.Name.asc(),
#             docs.fields.RegisteredOn.desc()
#         )
#         return ret
#

#
#     def get_item_with_cache(self, app_name):
#         from cy_docs import DocumentObject
#         cache_key = f"{__file__}/{type(self).__name__}/get_item_with_cache/{app_name}"
#         ret = self.memcache_service.get_object(key=cache_key,cls=DocumentObject)
#         if ret:
#             return ret
#         else:
#             qr = self.get_queryable()
#             app = qr.context.find_one(
#                 app_name=app_name
#             )
#             self.memcache_service.set_object(
#                 key=cache_key,
#                 data = app
#             )
#             return app
#

#
#     def save_azure_access_token(self,
#                                 request,
#                                 app_name: str,
#                                 azure_access_token: str,
#                                 azure_refresh_token: str,
#                                 azure_token_id: str,
#                                 azure_verify_code: str):
#         docs = self.db_connect.db('admin').doc(App)
#         doc = docs.fields
#         ret = docs.context.update(
#             doc.Name == app_name,
#             doc.AppOnCloud.Azure.AccessToken << azure_access_token,
#             doc.AppOnCloud.Azure.RefreshToken << azure_refresh_token,
#             doc.AppOnCloud.Azure.TokenId << azure_token_id,
#             doc.AppOnCloud.Azure.AuthCode << azure_verify_code
#
#         )
#         cache_key = f"{__file__}/{type(self).__name__}/get_item_with_cache/{app_name}"
#         self.memcache_service.remove(cache_key)
#         return ret
#
#     def update(self,
#                request,
#                Name: str,
#                Description: typing.Optional[str] = None,
#                azure_app_name: typing.Optional[str] = None,
#                azure_client_id: typing.Optional[str] = None,
#                azure_tenant_id: typing.Optional[str] = None,
#                azure_client_secret: typing.Optional[str] = None,
#                azure_auth_code: typing.Optional[str] = None,
#                azure_client_is_personal_acc: typing.Optional[bool] = False):
#         docs = self.db_connect.db('admin').doc(App)
#         doc = docs.fields
#         # url_azure_login = None
#         url_azure_personal_account_login = None
#         url_azure_business_account_login = None
#
#         if isinstance(azure_client_id, str):
#
#             redirect_url = f"{cy_web.get_host_url(request)}/api/{Name}/azure/after_login"
#
#             # url_azure_login = self.ms_app.get_login_url(
#             #     client_id=azure_client_id,
#             #     redirect_uri= f"{cy_web.get_host_url()}/api/{Name}/azure/after_login"
#             # )
#             # url_azure_login+=f"?lv-file-app-name={Name}"
#         ret = docs.context.update(
#             doc.Name == Name,
#             doc.Description << Description,
#             doc.ModifiedOn << datetime.datetime.utcnow(),
#             doc.AppOnCloud.Azure.Name << azure_app_name,
#             doc.AppOnCloud.Azure.ClientId << azure_client_id,
#             doc.AppOnCloud.Azure.TenantId << azure_tenant_id,
#             doc.AppOnCloud.Azure.PersonalAccountUrlLogin << url_azure_personal_account_login,
#             doc.AppOnCloud.Azure.BusinessAccountUrlLogin << url_azure_business_account_login,
#             doc.AppOnCloud.Azure.ClientSecret << azure_client_secret,
#             doc.AppOnCloud.Azure.IsPersonal << azure_client_is_personal_acc,
#             doc.AppOnCloud.Azure.AuthCode << azure_auth_code,
#             doc.NameLower << Name.lower()
#
#         )
#         agg = docs.context.aggregate().project(
#             cy_docs.fields.AppId >> docs.fields.Id,
#             docs.fields.Name,
#             docs.fields.Description,
#             docs.fields.Domain,
#             docs.fields.LoginUrl,
#             docs.fields.ReturnUrlAfterSignIn,
#             docs.fields.ReturnSegmentKey,
#             cy_docs.fields.Apps >> docs.fields.AppOnCloud,
#             docs.fields.AppOnCloud
#
#         )
#         ret_app = agg.match((doc.NameLower == Name.lower()) | (doc.Name == Name)).first_item()
#         # if ret_app is None:
#         #     ret_app = agg.match(docs.fields.Name == Name).first_item()
#         cache_key = f"{__file__}/{type(self).__name__}/get_item_with_cache/{Name}"
#         self.memcache_service.remove(cache_key)
#         from cy_fw_microsoft.services.account_services import AccountService
#         acc= cy_kit.singleton(AccountService)
#         acc.clear_token_cache(
#             app_name= Name
#         )
#
#         return ret_app
#

