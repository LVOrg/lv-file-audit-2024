import _json
__url__ = None

import json


def config_server(url:str):
    global __url__
    __url__ = url


def call_suggestion(txt:str)->str:
    if __url__ is None:
        raise Exception(f"Please call {config_server}")
    import requests
    response = requests.post(f"{__url__}/suggest",json.dumps(txt))
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Can not call {__url__}/suggest")

config_server("http://172.16.13.72:8000")
fx=call_suggestion("kiem tra tieng viet khong dau")
print(fx)
