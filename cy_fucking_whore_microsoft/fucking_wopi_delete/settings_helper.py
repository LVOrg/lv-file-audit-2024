import cy_kit
from cy_xdoc.services.apps import AppServices
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException,ErrorEnum
class SettingsHelper:
    client_id: str
    client_secret: str
    AuthorizationUri = "https://login.microsoftonline.com"
    Authority = f"{AuthorizationUri}/common"
    AADGraphResourceId = "https://graph.windows.net"
    MicrosoftGraphResourceId = "https://graph.microsoft.com"
    Audience = "https://officewopi.azurewebsites.net"

class SettingService:
    def __init__(self,
                 app_service = cy_kit.singleton(AppServices)):
        self.app_service = app_service
    def get_setting(self,app_name:str)->SettingsHelper:
        qr = self.app_service.get_queryable()
        app = self.app_service.get_item_with_cache(
            app_name=app_name
        )
        if app is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.APP_NOT_FOUND,
                message= f"App {app_name} was not found"
            )
        if app[qr.fields.AppOnCloud.Azure.ClientId] is None:
            raise FuckingWhoreMSApiCallException(
                code=ErrorEnum.REQUIRE_LINK_TO_MICROSOFT,
                message=f"App {app_name} does not link to MS"
            )

        ret = SettingsHelper()
        ret.client_id = app[qr.fields.AppOnCloud.Azure.ClientId]
        ret.client_secret = app[qr.fields.AppOnCloud.Azure.ClientSecret]
        return ret


