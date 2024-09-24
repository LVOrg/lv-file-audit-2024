import typing
import json
T=typing.TypeVar("T")
import requests
URL = 'https://graph.microsoft.com/v1.0/'
def call_ms_func(method: str,
                 api_url: str,
                 token: str,
                 body,
                 request_content_type: typing.Optional[str]=None)->typing.Tuple[typing.Union[dict,None],typing.Union[dict,None]]:
    """
    The bullshit function use for Whore-Microsoft-online calling.
    Official Exception is cy_azure.fwcking_ms.caller.ApiCallException
    :param method: any in post, get, patch, delete,..
    :param api_url: example 'me','me/drive
    :param token: somehow thy must get that shit token from Whore-Microsoft-online
    :param body: if api from  Whore-Microsoft-Graph-API
    :param return_type: This shit function will try parse from json response from Whore-Microsoft-online into class type
    :return:
    """
    http_method = getattr(requests, method.lower())
    if not callable(http_method):
        raise Exception(f"{method} is in valid http request method")
    HEADERS = {'Authorization': 'Bearer ' + token}
    if request_content_type is not None:
        HEADERS["Content-Type"] = request_content_type
    if body:
        if request_content_type == "application/json":
            response = http_method(URL + api_url, headers=HEADERS, json=body)
        else:
            response = http_method(URL + api_url, headers=HEADERS, data=body)

    else:
        response = http_method(URL + api_url, headers=HEADERS)
    try:
        res = response.json()
    except:
        res = {}
    if isinstance(res.get("error"),dict):
        if res.get("error").get("code"):
            return None, dict(Code=res.get("error").get("code"), Message= res.get("error").get("message"))

    return res, None
