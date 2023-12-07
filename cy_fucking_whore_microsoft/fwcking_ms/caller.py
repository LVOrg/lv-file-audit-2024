import typing

import requests
import json
import urllib

URL = 'https://graph.microsoft.com/v1.0/'
from typing import Generic, TypeVar

T = TypeVar('T')
from enum import Enum


class ErrorEnum(Enum):
    IMPROPER_MICROSOFT_APP_REGISTER = "IMPROPER_MICROSOFT_APP_REGISTER"
    REQUIRE_LOGIN_TO_MICROSOFT = "REQUIRE_LOGIN_TO_MICROSOFT"
    APP_NOT_FOUND = "APP_NOT_FOUND"
    REQUIRE_LINK_TO_MICROSOFT = "REQUIRE_LINK_TO_MICROSOFT"


class FuckingWhoreMSApiCallException(Exception):
    def __init__(self, message, code: typing.Union[str, ErrorEnum], http_status=None):
        self.message = message
        if isinstance(code, ErrorEnum):
            self.code = code.value
        else:
            self.code = code
        self.status = http_status

    def __str__(self):
        if self.status is None:
            return self.message + "\n" + self.code
        else:
            return self.message + "\n" + self.code + "\nupstream-error:" + self.status


def call_ms_func(method: str, api_url: str, token: str, body, return_type: T,
                 request_content_type: typing.Optional[str]) -> T:
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
    if 200 <= response.status_code < 300:
        response = json.loads(response.text)
        if return_type == dict:
            return response
        ret = return_type()
        for k, v in response.items():
            ret.__dict__[k] = v
        return ret
    else:
        ex = Exception(f'Unknown error! See response for more details. {response.text}')
        try:
            error = json.loads(response.text)
            error_message = error["error"].get("message")
            error_code = error["error"].get("code")
            ex = FuckingWhoreMSApiCallException(
                message=error_message,
                code=error_code,
                http_status=response.status_code
            )
        except:
            pass
        raise ex


def refresh_token(client_id: str, client_secret: str, refresh_token: str,
                  scopes: typing.Optional[typing.List[str]] = None):
    __scope__ = ['Sites.ReadWrite.All',
                 'Files.ReadWrite.All',
                 'directory.ReadWrite.All',
                 'Files.Read',
                 'Files.Read.All',
                 'Files.ReadWrite',
                 'Files.ReadWrite.All']
    _scopes = list(set(__scope__ + (scopes or [])))
    __scope_str__ = urllib.parse.quote(" ".join(_scopes), 'utf8')
    headers = {
        # "Content-Type": "application/x-www-form-urlencoded",
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        'scope': __scope_str__
    }

    response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token",
                             headers=headers,
                             data=headers,
                             verify=False)

    if response.status_code == 200:
        print("New access token:", response.json()["access_token"])
    else:
        ex = Exception(f'Unknown error! See response for more details. {response.text}')
        try:
            error = json.loads(response.text)
            error_message = error["error"].get("message")
            error_code = error["error"].get("code")
            ex = FuckingWhoreMSApiCallException(message=error_message, code=error_code)
        except:
            pass
        raise ex
