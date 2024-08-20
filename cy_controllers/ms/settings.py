import typing

from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Body,

)

from cy_controllers.common.base_controller import BaseController

router = APIRouter()
controller = Controller(router)

from cy_xdoc.auths import Authenticate
@controller.resource()
class MSSettings(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.router.post(
        path="/api/{app_name}/ms/settings/update"
    )
    def settings_update(self,app_name:str,tenantId:str=Body(embed=True), clientId:str=Body(embed=True),clientSecret:str=Body(embed=True)):
        return self.ms_common_service.settings_update(
            app_name=app_name,
            tenant_id = tenantId,
            client_id = clientId,
            client_secret=clientSecret,
            request = self.request

        )

    @controller.router.post(
        path="/api/{app_name}/ms/settings/get"
    )
    async def settings_get(self, app_name: str):

        tenant_id,client_id,client_secret,redirect_url = await self.ms_common_service.settings_get(app_name)
        return dict(
            tenantId= tenant_id,
            clientID=client_id,
            clientSecret=client_secret,
            redirectUrl=redirect_url
        )

    @controller.router.post(
        path="/api/{app_name}/ms/auth/get-login-url"
    )
    def get_login_url(self, app_name: str, scopes: typing.List[str] = Body(...)):
        url, error = self.ms_common_service.get_url(app_name=app_name, scopes=scopes)
        if error:
            return error
        else:
            return url
