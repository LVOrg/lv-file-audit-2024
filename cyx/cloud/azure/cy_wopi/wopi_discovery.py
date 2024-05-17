"""
This library will work with
https://onenote.officeapps.live.com/hosting/discovery or
https://ffc-onenote.officeapps.live.com/hosting/discovery
What those urls return?
Those url return how many apps in officeapps.live.com from Microsoft have
and what action in each of app in their apps support. Such as "view", "edit","comment",...
with app name, action name and extension doc we can get urlsrc.
urlsrc give a format of url we can use to embed Web Platform of app
Example call
get_action("word","edit","docx")
We will get urlsrc like below:
'https://FFC-word-edit.officeapps.live.com/we/wordeditorframe.aspx?<ui=UI_LLCC&><rs=DC_LLCC&><dchat=DISABLE_CHAT&><hid=HOST_SESSION_ID&><sc=SESSION_CONTEXT&><wopisrc=WOPI_SOURCE&><showpagestats=PERFSTATS&><IsLicensedUser=BUSINESS_USER&><actnavid=ACTIVITY_NAVIGATION_ID&>'

Production	https://onenote.officeapps.live.com/hosting/discovery
Test/Dogfood	https://ffc-onenote.officeapps.live.com/hosting/discovery

"""
import typing
import urllib.parse

import requests
import xmltodict

__url_of_production__ = "https://onenote.officeapps.live.com/hosting/discovery"
__url_of_test__ = "https://ffc-onenote.officeapps.live.com/hosting/discovery"
__cache__ = {}
__is_production__ = False


def set_mode(is_production: bool):
    global __is_production__
    __is_production__ = __is_production__


def get_discovery(nocache=False) -> dict:
    if nocache:
        response = requests.get(__url_of_test__)
        content = response.content
        ret = xmltodict.parse(content)
        return ret
    global __cache__
    if __is_production__:
        __url__ = __is_production__
    else:
        __url__ = __url_of_test__
    if __cache__.get(__url__) is None:
        response = requests.get(__url__)

        # Get the content from the response.
        content = response.content
        ret = xmltodict.parse(content)
        __cache__[__url__] = ret
        return ret
    else:
        return __cache__[__url__]


"""
fx['wopi-discovery']['net-zone']['apps']
"""

action_url_map= dict(
    BUSINESS_USER = 1,
    DISABLE_CHAT= True,
    DISABLE_ASYNC = True,
    EMBEDDED = True,
    FULLSCREEN = True
)

def get_app(name: str)->typing.Optional[dict]:
    """
    get app from officeapps.live.com
    :param name:
    :return:
    """
    items = [x for x in get_discovery()['wopi-discovery']['net-zone']['app'] if x["@name"].lower() == name.lower()]
    if len(items)>0:
        return items[0]
    else:
        return None


def get_action(app_name: str, action: str, ext_file: str)->typing.Optional[dict]:
    """
    get action
    :param app_name:
    :param action:
    :param ext_file:
    :return:
    """
    app_actions = get_app(app_name)["action"]
    items = [x for x in app_actions
             if x["@name"].lower() == action.lower() and \
             x["@ext"].lower() == ext_file.lower()
             ]
    if len(items) > 0:
        return items[0]
    else:
        return None


def get_action_url(app_name, action, ext_file,wopi_source:str,config:typing.Optional[dict] = None):
    config= config or action_url_map
    action_dict = get_action(app_name=app_name,action=action,ext_file=ext_file)
    url = action_dict["@urlsrc"]
    items = url.split("?")
    primary_url = items[0]
    params_url = str(items[1])
    ret= params_url
    items = params_url.lstrip().rstrip(">").split("&><")
    par_urls= ""
    for x in items:
        k,v = tuple(x.split("="))
        if v!="WOPI_SOURCE":
            if config.get(v):
                par_urls+=f"{k}={config.get(v)}&"
        else:
            par_urls += f"{k}={urllib.parse.quote(wopi_source)}&"
    par_urls = par_urls.rstrip("&")
    ret = primary_url+"?"+par_urls
    return ret


def get_hash_discovery(nocache=False):
    dict_data = get_discovery(nocache)
    ret = dict_data['wopi-discovery']['net-zone']
    hash_ret = {}
    for x in ret['app']:
        for a in x['action']:
            key=f"{x['@name'].lower()}/{a['@name'].lower()}/{a.get('@ext','-')}"
            hash_ret[key]=a
    return hash_ret

def query_app(str_query:str,nocache=False):
    dataset = get_hash_discovery(nocache)
    str_query_lower = str_query.lower()
    _ret = [{k:v} for k,v in dataset.items() if k.startswith(str_query_lower)]
    ret = dict()
    for x in _ret:
        ret= {**ret,**x}
    return ret
