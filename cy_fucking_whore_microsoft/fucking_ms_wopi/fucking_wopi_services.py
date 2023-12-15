import typing

import requests
import xmltodict

import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
from cy_fucking_whore_microsoft.fucking_ms_wopi.fucking_wopi_models import (
    WopiAction,
    WopiActionContainer
)

URL_DISCOVERY = "https://ffc-onenote.officeapps.live.com/hosting/discovery"
from xml.etree import ElementTree as ET


class FuckingWopiService:
    def __init__(self, memcache_service=cy_kit.singleton(MemcacheServices)):
        self.memcache_service = memcache_service

    def get_discovery_info(self) -> typing.List[WopiAction]:
        cache_key = f"{__file__}/{type(self).__name__}/get_discovery_info"
        ret: WopiActionContainer = self.memcache_service.get_object(cache_key, WopiActionContainer)
        ret_data = []
        if not isinstance(ret,WopiActionContainer):
            res = requests.get(URL_DISCOVERY)
            if res.status_code == 200:
                root = xmltodict.parse(res.text, process_namespaces=True)
                for app in root['wopi-discovery']['net-zone']['app']:
                    for x in app["action"]:
                        data_item = WopiAction()
                        data_item.app = app["@name"]
                        data_item.fav_icon_url = app["@favIconUrl"]
                        data_item.check_license = True if app["@checkLicense"]=="true" else False
                        data_item.name = x["@name"]
                        data_item.ext = x.get("@ext")
                        data_item.progid = x.get("@progid")
                        data_item.is_default = x.get("@default") is not None
                        data_item.urlsrc = x.get("@urlsrc")
                        data_item.requires = x.get("requires")
                        ret_data+=[data_item]
                ret = WopiActionContainer()
                ret.items = ret_data
                self.memcache_service.set_object(cache_key,ret)
                return ret_data
        else:
            return ret.items
