import typing

import cy_docs
import cy_kit
from cyx.ms.ms_auth_services import MSAuthService
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.repository import Repository
from fastapi.requests import Request

class MSCommonService:
    def __init__(self,
                 ms_auth_service=cy_kit.singleton(MSAuthService),
                 memcache_services=cy_kit.singleton(MemcacheServices)
                 ):
        self.ms_auth_service = ms_auth_service
        self.memcache_services = memcache_services

    def get_url(self, app_name, scopes)->typing.Tuple[str,typing.Dict[str,str]]:
        """
        Get url login to Microsoft live. before get function will check scopes
        :param app_name:
        :param scopes:
        :return:
        """
        raise NotImplemented()

    def settings_update(self, app_name:str, tenant_id:str, client_id:str, client_secret:str, request:Request)->typing.Dict[str,str]|None:
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
        cache_key = f"{type(self).__module__}/{type(self).__name__}/{app_name}"
        host_name = request.url.hostname
        url_endpoint = request.url.path.split('/')[1]
        redirect_url =  f"https://{host_name}/{url_endpoint}/api/{app_name}/after-ms-login"
        db_context = Repository.apps.app("admin").context
        db_context.update(
            Repository.apps.fields.Name==app_name,
            Repository.apps.fields.AppOnCloud.Azure.ClientId<<client_id,
            Repository.apps.fields.AppOnCloud.Azure.TenantId << tenant_id,
            Repository.apps.fields.AppOnCloud.Azure.ClientSecret << client_secret,
            Repository.apps.fields.AppOnCloud.Azure.RedirectUrl << redirect_url
        )
        return None
    def settings_get(self,app_name)->typing.Tuple[str|None,str|None,str|None]:
        """
        The fucking insane function will return all setting for MS contacting  which has been saved by using  MSCommonService.settings_update
        :param app_name:
        :return: tenant_id,client_id,client_secret
        """
        raise NotImplemented()