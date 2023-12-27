"""
https://ffc-onenote.officeapps.live.com/hosting/discovery
"""
import cy_kit

WORD_EDIT_OFFICE_APP = "https://word-edit.officeapps.live.com/we/wordeditorframe.aspx"
WORD_VIWER_FRAME ="https://FFC-word-view.officeapps.live.com/wv/wordviewerframe.aspx"
#https://word-view.officeapps.live.com/wv/wordviewerframe.aspx
WORD_VIWER_FRAME ="https://word-view.officeapps.live.com/wv/wordviewerframe.aspx"
WORD_VIWER_FRAME = f'https://FFC-word-view.officeapps.live.com/wv/wordviewerframe.aspx'
from urllib import parse
import cy_web
from cy_fucking_whore_microsoft.services.account_services import AccountService

class Office365Service:
    def __init__(self, fucking_account_service = cy_kit.singleton(AccountService)):
        self.fucking_account_service = fucking_account_service

    def get_embed_iframe_url(self, app_name: str,request, upload_id: str,include_token=True) -> str:
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
        token= self.fucking_account_service.acquire_token(
            app_name=app_name
        )
        token = parse.quote_plus(token)
        rel_api_url = f'api/{app_name}/wopi/files/{upload_id}'

        url_from_out_server = f"{cy_web.get_host_url(request)}/{rel_api_url}"
        if include_token:
            ret = f"{WORD_VIWER_FRAME}?embed=1&wopisrc={parse.quote_plus(url_from_out_server)}&access_token={token}"
        else:
            ret = f"{WORD_VIWER_FRAME}?embed=1&wopisrc={parse.quote_plus(url_from_out_server)}"
        return ret
