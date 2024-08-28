import pathlib
import typing
import uuid

from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
    responses,
    Body
)

import cy_web
from cy_xdoc.auths import Authenticate
import hashlib
import base64
import os

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.wopi_models import WopiFileInfo

WOPI_FILE_DIR = pathlib.Path(__file__).parent.parent.parent.__str__()
from cy_controllers.models.files import ErrorInfo
from pydantic import BaseModel


class GetEmbedUrlResult(BaseModel):
    Error: typing.Optional[ErrorInfo]
    Data: typing.Optional[str]


@controller.resource()
class Office365Controller(BaseController):
    # dependencies = [
    #     Depends(Authenticate)
    # ]
    @controller.route.post(
        "/api/{app_name}/office365/get_embed_url", summary="Re run index search",
        tags=["WOPI"]
    )
    def get_embed_url(self, app_name: str, upload_id: str = Body(embed=True)) -> GetEmbedUrlResult:
        """
        Get file info. Implements the CheckFileInfo WOPI call
        :param app_name:
        :param fileid:
        :return:
        """

        ret_url,error = self.ms_office_365_service.get_embed_iframe_url(
            app_name=app_name,
            upload_id=upload_id,
            request=self.request
        )
        if error:
            ret= GetEmbedUrlResult()
            ret.Error=ErrorInfo()
            ret.Error.Code=error.get("Code")
            ret.Error.Message = error.get("Message")
            return ret
        else:
            ret = GetEmbedUrlResult()
            ret.Data=ret_url
            return ret


        # ret = self.fucking_office_365_service.get_embed_iframe_url(
        #     app_name=app_name,
        #     upload_id=upload_id,
        #     request=self.request
        # )
        # return ret

    @controller.route.get(
        "/api/{app_name}/office365/view/{upload_id}", summary="Re run index search",tags=["WOPI"]
    )
    def office365_view(self, app_name: str, upload_id: str):
        """

        :param app_name:
        :param upload_id:
        :return:
        """
        from cy_fw_microsoft.ssl_utils.fucking_utils import generate_access_token

        access_token = self.fucking_azure_account_service.acquire_token(
            app_name=app_name
        )
        wopi_access_token_info = generate_access_token(
            issuer=cy_web.get_host_url(self.request),
            audience=f"{cy_web.get_host_url(self.request)}/lvfile/api/{app_name}/wopi",
            user="nttlong@lacviet.com.vn",
            docid=upload_id,
            pfx_password="dxwopi"
        )
        access_token = str(uuid.uuid4())

        access_token_ttl = ""
        src = self.fucking_office_365_service.get_embed_iframe_url(app_name=app_name, upload_id=upload_id,
                                                                   include_token=False)
        # wopi_access_token_info.access_token=access_token
        ret_html = (f'<form id="office_form" name="office_form" target="office_frame" action="{src}" method="post">'
                    f'<input name="access_token" value="{access_token}" type="hidden" />'
                    f'<input name="access_token_ttl" value="{wopi_access_token_info.access_token_ttl}" type="hidden"/>'
                    f'</form>'
                    f'<span id="frameholder"></span>'
                    f'<script type="text/javascript">'
                    f'var frameholder = document.getElementById("frameholder");'
                    f'var office_frame = document.createElement("iframe");'
                    f'office_frame.name = "office_frame";'
                    f'office_frame.id ="office_frame";'
                    f'office_frame.title = "Office Online Frame";'
                    f'office_frame.setAttribute("allowfullscreen", "true");'
                    f'frameholder.appendChild(office_frame);'
                    f'office_frame.width="100%";'
                    f'office_frame.height="100%";'
                    f'document.getElementById("office_form").submit();'
                    f'</script>')
        res = responses.HTMLResponse(
            content=ret_html
        )
        return res

    @controller.route.get(
        "/api/discovery", summary="Re run index search"
    )
    def discovery(self):
        for x in self.fucking_wopi_service.get_discovery_info():
            yield x.__dict__

    @controller.route.get(
        "/api/signing_key", summary="Re run index search"
    )
    def signing_key(self):
        from cy_fw_microsoft.fucking_ms_wopi.fucking_wopi_security import get_signing_key
        return get_signing_key()
