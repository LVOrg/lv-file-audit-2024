import _json

__url__ = None

import json


def config_server(url: str):
    global __url__
    __url__ = url


def call_suggestion(txt: str) -> str:
    if __url__ is None:
        raise Exception(f"Please call {config_server}")
    import requests
    response = requests.post(f"{__url__}/suggest", json.dumps(txt),timeout=5)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Can not call {__url__}/suggest")
