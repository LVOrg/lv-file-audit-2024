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


