__url__ = "https://ffc-onenote.officeapps.live.com/hosting/discovery"

import requests
import xmltodict
__cache__ = None

def get_discovery() -> dict:
    global  __cache__
    if __cache__ is None:
        response = requests.get(__url__)

        # Get the content from the response.
        content = response.content
        ret = xmltodict.parse(content)
        __cache__  = ret
        return ret
    else:
        return __cache__


"""
fx['wopi-discovery']['net-zone']['apps']
"""
def get_app(name:str):
    items = [x for x in get_discovery()['wopi-discovery']['net-zone']['app'] if x["@name"].lower()==name.lower()]
    return items[0]


def get_action(app_name:str,action:str,ext_file:str):
    app_actions = get_app(app_name)["action"]
    items =[x for x in  app_actions
            if x["@name"].lower()==action.lower() and \
               x["@ext"].lower() == ext_file.lower()
            ]
    if len(items)>0:
        return items[0]
    else:
        return None