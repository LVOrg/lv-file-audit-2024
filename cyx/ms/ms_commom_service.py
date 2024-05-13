import datetime
import typing

import cy_docs
import cy_kit
from cyx.ms.ms_auth_services import MSAuthService
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.repository import Repository
from fastapi.requests import Request
import requests

class MSAuthenticateInfo:
    access_token:str
    refresh_token:str
    id_token:str
    scope:str
    expires_in:str
    expire_on: datetime.datetime



class MSCommonService:
    def __init__(self,
                 ms_auth_service=cy_kit.singleton(MSAuthService),
                 memcache_services=cy_kit.singleton(MemcacheServices)
                 ):
        self.ms_auth_service = ms_auth_service
        self.memcache_services = memcache_services

    def get_url(self, app_name, scopes) -> typing.Tuple[str | None, typing.Dict[str, str] | None]:
        """
        Get url login to Microsoft live. before get function will check scopes
        :param app_name:
        :param scopes:
        :return:
        """
        tenant_id, client_id, client_secret, redirect_url = self.settings_get(app_name)
        token, roles = self.ms_auth_service.get_access_token_and_roles(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        if len(scopes) > 0 and not set(roles).issubset(roles):
            txt_scope = ",\n".join([f"'{x}'" for x in scopes])
            ms_scope = ",\n".join([f"'{x}'" for x in roles])
            return None, dict(
                code="InvalidScope",
                description=f"You acquire scopes [{txt_scope}] not in [{ms_scope}] of Application {tenant_id}, "
                            f"please verify your setting at  check https://portal.azure.com/"
            )
        graph_scopes = [f"https://graph.microsoft.com/{x}" for x in scopes]
        ret_url = self.ms_auth_service.get_url_login(
            client_id=client_id,
            scopes=graph_scopes,
            tenant_id=tenant_id,
            redirect_uri=redirect_url
        )
        return ret_url, None

    def settings_update(self, app_name: str, tenant_id: str, client_id: str, client_secret: str, request: Request) -> \
            typing.Dict[str, str] | None:
        """
        This fucking method save all info to database
        Heed: The function also cache all info to memcahed by using cyx.cache_service.memcache_service.MemcacheServices
        Phương pháp chết tiệt này lưu tất cả thông tin vào cơ sở dữ liệu
        Lưu ý: Chức năng này cũng lưu trữ tất cả thông tin vào memcahed bằng cách sử dụng cyx.cache_service.memcache_service.MemcacheServices
        :param app_name:
        :param tenant_id:
        :param client_id:
        :param client_secret:
        :param request:
        :return: None if everything are OK. else return dict describe hwo the fucking MS return error \n K
        hông có nếu mọi thứ đều ổn. khác thì trả về dict mô tả lỗi trả về MS chết tiệt
        """
        cache_key = self.get_cache_key(app_name)
        host_name = request.url.hostname
        url_endpoint = request.url.path.split('/')[1]
        redirect_url = f"https://{host_name}/{url_endpoint}/api/{app_name}/after-ms-login"
        db_context = Repository.apps.app("admin").context
        db_context.update(
            Repository.apps.fields.Name == app_name,
            Repository.apps.fields.AppOnCloud.Azure.ClientId << client_id,
            Repository.apps.fields.AppOnCloud.Azure.TenantId << tenant_id,
            Repository.apps.fields.AppOnCloud.Azure.ClientSecret << client_secret,
            Repository.apps.fields.AppOnCloud.Azure.RedirectUrl << redirect_url
        )
        self.memcache_services.set_dict(self.get_cache_key(app_name), dict(
            client_id=client_id,
            tenant_id=tenant_id,
            client_secret=client_secret,
            redirect_url=redirect_url
        ))
        return None

    def settings_get(self, app_name) -> typing.Tuple[str | None, str | None, str | None, str | None]:
        """
        The fucking insane function will return all setting for MS contacting  which has been saved by using
        MSCommonService.settings_update :param app_name: :return: tenant_id,client_id,client_secret,redirect_url
        """
        data = self.memcache_services.get_dict(self.get_cache_key(app_name))

        if isinstance(data, dict) and data.get("tenant_id") and data.get("client_id") and data.get(
                "client_secret") and data.get("redirect_url"):

            return data.get("tenant_id"), data.get("client_id"), data.get("client_secret"), data.get("redirect_url")
        else:
            data = Repository.apps.app("admin").context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.ClientId >> Repository.apps.fields.AppOnCloud.Azure.ClientId,
                cy_docs.fields.TenantId >> Repository.apps.fields.AppOnCloud.Azure.TenantId,
                cy_docs.fields.ClientSecret >> Repository.apps.fields.AppOnCloud.Azure.ClientSecret,
                cy_docs.fields.RedirectUrl >> Repository.apps.fields.AppOnCloud.Azure.RedirectUrl
            ).first_item()

            if data is None:
                return None, None, None, None
            else:

                self.memcache_services.set_dict(self.get_cache_key(app_name), dict(
                    client_id=data.ClientId,
                    tenant_id=data.TenantId,
                    client_secret=data.ClientSecret,
                    redirect_url=data.RedirectUrl
                ))
                return data.TenantId, data.ClientId, data.ClientSecret, data.RedirectUrl

    def get_cache_key(self, app_name):
        return f"{type(self).__module__}/{type(self).__name__}/{app_name}"

    def get_token_from_app_by_verify_code(self, app_name, verify_code) -> typing.Tuple[MSAuthenticateInfo|None,dict|None]:
        """
        The fucking function will verify code and  return access_token, refresh_token,id_token,scope
        :param app_name:
        :param verify_code:
        :return: access_token, refresh_token,id_token,scope,error
        """
        tenant_id, client_id, client_secret, redirect_url = self.settings_get(app_name)
        grant_type = "authorization_code"
        data = {
            "grant_type": grant_type,
            "code": verify_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_url

            # "scope": "https%3A%2F%2Fgraph.microsoft.com%2Fmail.read",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url_request = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        # if is_business_account:
        #     if tenant is None:
        #         raise Exception("tenant is require")
        #     url_request = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        # https://login.microsoftonline.com/13a53f39-4b4d-4268-8c5e-ae6260178923/oauth2/v2.0/token
        response = requests.post(url_request, data=data)

        if response.status_code == 200:
            res_json = response.json()
            expires_in = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(res_json["ext_expires_in"]))
            ret =MSAuthenticateInfo()
            for k,v in res_json.items():
                setattr(ret,k,v)
            ret.expire_on =expires_in
            return ret,None
        else:
            res_data = response.json()
            if res_data.get("error"):
                return None, dict(
                    error=res_data.get("error"),
                    description=res_data.get("error_description")
                )
            return None, response.json()

    def authenticate_update(self,
                            app_name:str,
                            access_token: str,
                            refresh_token: str,
                            id_token: str,
                            scope:str,
                            utc_expire: datetime.datetime):
        cache_key = f'{self.get_cache_key(app_name)}/auth'
        db_context = Repository.apps.app('admin').context
        db_context.update(
            Repository.apps.fields.Name == app_name,
            Repository.apps.fields.AppOnCloud.Azure.RefreshToken << refresh_token,
            Repository.apps.fields.AppOnCloud.Azure.AccessToken << access_token,
            Repository.apps.fields.AppOnCloud.Azure.TokenId << id_token,
            Repository.apps.fields.AppOnCloud.Azure.UtcExpire << utc_expire,
            Repository.apps.fields.AppOnCloud.Azure.Scope << scope
        )
        self.memcache_services.set_dict(cache_key, dict(
            refresh_token=refresh_token,
            access_token=access_token,
            id_token=id_token,
            utc_expire=utc_expire,
            scope = scope
        ))

    def authenticate_get(self, app_name) -> typing.Tuple[str | None, str | None, dict | None]:
        """
        The fucking function return access_token, refresh_token, error This method will return   access_token,
        refresh_token if they are in memcache else extract all those info from database then put to mecache and
        return them Phương thức này sẽ trả về access_token, Refresh_token nếu chúng ở trong memcache, nếu không thì
        trích xuất tất cả thông tin đó từ cơ sở dữ liệu rồi đưa vào memcache và trả về chúng :param app_name: :return:
        access_token, refresh_token, error
        """
        try:
            cache_key = f'{self.get_cache_key(app_name)}/auth'
            data = self.memcache_services.get_dict(cache_key)
            if (isinstance(data, dict)
                    and data.get("refresh_token")
                    and data.get("access_token")
                    and isinstance(data.get("utc_expire"), datetime.datetime)
                    and (data.get("utc_expire") - datetime.datetime.utcnow()).total_seconds() > 5):

                return data.get("access_token"), data.get("refresh_token"), None
            else:
                data = Repository.apps.app("admin").context.aggregate().match(
                    Repository.apps.fields.Name == app_name
                ).project(
                    cy_docs.fields.access_token >> Repository.apps.fields.AppOnCloud.Azure.AccessToken,
                    cy_docs.fields.refresh_token >> Repository.apps.fields.AppOnCloud.Azure.RefreshToken,
                    cy_docs.fields.utc_expire >> Repository.apps.fields.AppOnCloud.Azure.UtcExpire,
                    cy_docs.fields.client_id >> Repository.apps.fields.AppOnCloud.Azure.ClientId,
                    cy_docs.fields.client_secret >> Repository.apps.fields.AppOnCloud.Azure.ClientSecret,
                    cy_docs.fields.tenant_id >> Repository.apps.fields.AppOnCloud.Azure.TenantId,
                    cy_docs.fields.scope >> Repository.apps.fields.AppOnCloud.Azure.Scope,
                    cy_docs.fields.redirect_uri >> Repository.apps.fields.AppOnCloud.Azure.RedirectUrl
                ).first_item()

                if data is None:
                    return None, None, dict(error="NotFound",
                                            description=f"MS Azure settings was not found in app {app_name}. Please contact administrator to re-config that settings")
                else:
                    self.memcache_services.set_dict(cache_key, dict(
                        refresh_token=data.refresh_token,
                        access_token=data.access_token,
                        utc_expire=data.utc_expire,
                        scope = data.scope

                    ))
                    if (data.utc_expire - datetime.datetime.utcnow()).total_seconds() > 5:
                        return data.access_token, data.refresh_token, None
                    else:
                        access_token, utc_expire,error = self.ms_auth_service.get_access_token_from_refresh_token(
                            client_id=data.client_id,
                            client_secret = data.client_secret,
                            tenant_id= data.tenant_id,
                            refresh_token= data.refresh_token,
                            scope=data.scope,
                            redirect_uri= data.redirect_uri
                        )
                        if error:
                            return None,None, error
                        else:
                            self.memcache_services.set_dict(cache_key, dict(
                                refresh_token=data.refresh_token,
                                access_token=access_token,
                                utc_expire=utc_expire,
                                scope = data.scope,
                            ))
                            Repository.apps.app("admin").context.update(
                                Repository.apps.fields.Name==app_name,
                                Repository.apps.fields.AppOnCloud.Azure.AccessToken << access_token,
                                Repository.apps.fields.AppOnCloud.Azure.UtcExpire << utc_expire
                            )
                            return access_token, utc_expire, None


        except Exception as ex:
            return None, None, dict(error="system", description=repr(ex))

    def call_graph_api(self, app_name: str, method: str, grap_api: str, data: dict |bytes| None,content_type:str=None) -> typing.Tuple[
        typing.Any, typing.Dict]:
        """
        Call grap api example call_graph_api(app_name='app-name',method='post',grap_api='me/sendMail')"
        see https://developer.microsoft.com/en-us/graph/graph-explorer for more detail
        :param app_name: tenant name
        :param method: post,get,put, patch,delete
        :param grap_api: example me/sendMail
        :param data: dictionary data see https://developer.microsoft.com/en-us/graph/graph-explorer for more detail
        :return:
        """
        url = f"https://graph.microsoft.com/v1.0/{grap_api}"
        access_token, refresh_token, error = self.authenticate_get(app_name)
        if error:
            return error
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": content_type or "application/json"
        }
        response = None
        try:
            if isinstance(data, dict) or isinstance(data,bytes):
                response = getattr(requests, method)(url, headers=headers, json=data)
            else:
                response = getattr(requests, method)(url, headers=headers)
            try:
                res_data = response.json()
                if res_data.get("error"):
                    if isinstance(res_data.get("error"), str):
                        return None, dict(error=res_data.get("error"), description=res_data.get("error_description"))
                    elif isinstance(res_data.get("error"), dict):
                        return None, dict(error=res_data.get("error").get("code"),
                                          description=res_data.get("error_description"))
                return res_data, None
            except:
                return response.text, None

        except Exception as e:
            return None, dict(error="System", description=repr(e))
