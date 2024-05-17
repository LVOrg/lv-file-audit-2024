import typing

import cy_kit
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
from cyx.cloud.azure.azure_utils import call_ms_func
from urllib import parse
import cy_web
from  fastapi.requests import Request
from cyx.cloud.azure.cy_wopi.wopi_discovery import query_app
from cyx.repository import Repository
from cyx.cloud.azure.cy_wopi import wopi_url_placeholders
WORD_EDIT_OFFICE_APP = "https://word-edit.officeapps.live.com/we/wordeditorframe.aspx"
WORD_VIWER_FRAME ="https://FFC-word-view.officeapps.live.com/wv/wordviewerframe.aspx"
#https://word-view.officeapps.live.com/wv/wordviewerframe.aspx
WORD_VIWER_FRAME ="https://word-view.officeapps.live.com/wv/wordviewerframe.aspx"
WORD_VIWER_FRAME = f'https://FFC-word-view.officeapps.live.com/wv/wordviewerframe.aspx'

class MSOffice365Service:
    def __init__(self, azure_utils_service: AzureUtilsServices = cy_kit.singleton(AzureUtilsServices)):
        self.azure_utils_service = azure_utils_service
    def get_embed_iframe_url(self, app_name: str,request:Request, upload_id: str,include_token=True) -> typing.Tuple[str|None,dict|None]:
        """
        http://word-edit.officeapps.live.com/we/wordeditorframe.aspx?WOPISrc=http%3a%2f%2flocalhost%3a32876%2fapi%2fwopi%2ffiles%2ftest.docx&access_token=XskWxXK0Nro%3dhwYoiCFehrYAx85XQduYQHYQE9EEPC6EVgqaMiCp4%2bg%3d
        :return:
        """
        #https://ffc-onenote.officeapps.live.com/hosting/discovery
        #https://FFC-word-view.officeapps.live.com/wv/wordviewerframe.aspx?
        # <ui=UI_LLCC&>
        # <rs=DC_LLCC&>
        # <dchat=DISABLE_CHAT&>
        # <hid=HOST_SESSION_ID&>
        # <sc=SESSION_CONTEXT&>
        # <wopisrc=WOPI_SOURCE&>
        # <showpagestats=PERFSTATS&><IsLicensedUser=BUSINESS_USER&><actnavid=ACTIVITY_NAVIGATION_ID&
        token_info,error = self.azure_utils_service.acquire_token(app_name)
        if error:
            return None,error
        # token= self.fucking_account_service.acquire_token(
        #     app_name=app_name
        # )
        token = parse.quote_plus(token_info.access_token)
        rel_api_url = f'api/{app_name}/wopi/files/{upload_id}'
        full_api_url = cy_web.get_host_url(request)+"/"+rel_api_url+"?access_token=123456789"

        upload_item = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.Id==upload_id
        )
        if not upload_item:
            return None, dict(Code="ItemNotFound",Message=f"{upload_id} was not found in {app_name}")
        query_action = f"word/edit/{upload_item[Repository.files.fields.FileExt]}"
        action = query_app(query_action)
        url_play_ack= action[query_action]['@urlsrc']
        placeholders = url_play_ack.split('?<')[1].split('&><')
        url_root =  url_play_ack.split('?')[0]
        ret_url =url_root+"?"
        for p in wopi_url_placeholders.placeholders:
            if p in url_play_ack:
                val = wopi_url_placeholders.get_placeholder_value(p)
                if val:
                    ret_url+=val+"&"
        ret_url+="wopisrc="+parse.quote_plus(full_api_url)
        return ret_url,None
        # for x in placeholders:
        #     if '=' in x:
        #         placeholders_key = x.split('=')[1]
        #         print(x)
        #         print(wopi_url_placeholders.get_placeholder_value(x))
        #         request_key = x.split('=')[0]
        #         print(placeholders_key)
        #         val =wopi_url_placeholders.get_placeholder_value(placeholders_key)
        #         if val:
        #             print(f"{request_key}={val}&")
        #             ret_url+= f"{request_key}={val}&"
        # ret_url= ret_url.rstrip('&')
        # url_from_out_server = f"{cy_web.get_host_url(request)}/{rel_api_url}"
        # if include_token:
        #     ret = f"{WORD_VIWER_FRAME}?embed=1&wopisrc={parse.quote_plus(url_from_out_server)}&access_token={token}"
        # else:
        #     ret = f"{WORD_VIWER_FRAME}?embed=1&wopisrc={parse.quote_plus(url_from_out_server)}"
        # return ret