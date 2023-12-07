import typing

import requests

import json

import urllib3, urllib
from fastapi import (
    FastAPI, Request
)

urllib3.disable_warnings()

__url_grap_v10_me__ = "https://graph.microsoft.com/v1.0/me"
__url_login_microsoftonline__ = "https://login.microsoftonline.com"
__scope__ = [
    # 'openid',
    # 'offline_access',
    # # 'https://contoso.com/.default',
    # 'User.ReadWrite.All',
    # 'wl.signin', 'wl.offline_access', 'onedrive.readwrite'
    # "https://graph.microsoft.com/.default"
]
class AzureTokeResultInfo:
    access_token: typing.Optional[str]
    id_token : typing.Optional[str]
    refresh_token: typing.Optional[str]
    token_type: typing.Optional[str]
    scope: typing.Optional[str]


def get_user_info(access_token: typing.Optional[str]):
    """
    This function return User Info after successful MS Azue Login
    this function require access_token
    In order to get access_token, thy must use an url from get_login_url.
    Use that URL from browser, the browser will redirect to FastAPI server according by return_url in get_login_url
    IMPORTANCE:
        Thy must handle return_url in get_login_url in thee server
        The most fucking cool to do that is: implement an API to handle return_url looks like these:
        return_url = "/api/after_login_azue
        @router(url=return_url)
        def after__login_azure(request:FastAPI.Request):
            #call is_login_azure_ok(request) to make sure use already login to azure
            #call get_verify_code(request) to get verify_code. That verify_code really important to get access_token
    QUAN TRỌNG: Bạn phải xử lý return_url trong get_login_url trên máy chủ của bạn.
                Cách làm hay nhất để thực hiện điều này là: triển khai API để xử lý return_url như sau:
                return_url = "/api/after_login_azue
                @router(url=return_url)
                def after__login_azure(request:FastAPI.Request):
                    #call is_login_azure_ok(request) để đảm bảo người dùng đã đăng nhập Azure
                    #call get_verify_code(request) để lấy verify_code. Verify_code đó thực sự quan trọng để lấy mã thông
                    báo truy cập.
    :param access_token:
    :return:
    """
    assert isinstance(access_token, str), "access_token must be string"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(__url_grap_v10_me__, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Error: {response.status_code}")


def post_form_data(url: str, post_data: typing.Optional[typing.Dict]) -> typing.Optional[typing.Dict]:
    """
    Post a basic form data
    :param url:
    :param post_data:
    :return:
    """
    data = {key: value for key, value in post_data.items()}
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=encoded_data, headers=headers)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        return response_data
    else:
        raise Exception(f"Error: {response.status_code}")


def get_login_url(return_url: str, client_id: str, tenant: str,scopes:typing.Optional[typing.List[str]]=[],is_personal_account:bool=False):
    """
    get login URL of microsoft online
    All require factors to do that are return_url, client_id, tenant must be registered before use
    :param return_url:
    :param client_id:
    :param tenant:
    :return:
    """
    rel_logon_urlrel_logon_url = f"{tenant}/oauth2/v2.0/authorize"
    _scopes =list(set(__scope__+scopes+[f"api://{client_id}/Admin"]))
    for x in _scopes:
        print(x)
    encoded_return_url = urllib.parse.quote_plus(return_url)
    __scope_str__ = urllib.parse.quote(" ".join(_scopes), 'utf8')
    #https://login.microsoftonline.com/13d23acb-69f3-4651-98fe-76e95992f779/oauth2/v2.0/authorize
    #https://login.microsoftonline.com/13d23acb-69f3-4651-98fe-76e95992f779/oauth2/authorize
    if is_personal_account:
        tenant="consumers"
    claims='&claims=%7B%22access_token%22%3A%7B%22acrs%22%3A%7B%22essential%22%3Atrue%2C%22value%22%3A%22c1%22%7D%7D%7D'
    # fx=f'https://login.microsoftonline.com/testdirectory.onmicrosoft.com/adminconsent?client_id={client_id}&redirect_uri={encoded_return_url}'
    login_url = f"{__url_login_microsoftonline__}/{tenant}/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={encoded_return_url}&scope={__scope_str__}"
    login_url = f"{__url_login_microsoftonline__}/{tenant}/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={encoded_return_url}&scope={__scope_str__}"
    # login_url = f"{__url_login_microsoftonline__}/{tenant}/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={encoded_return_url}&scope={__scope_str__}"
    # login_url =f"https://login.microsoftonline.com/{tenant}/adminconsent?client_id={client_id})&response_type=code&redirect_uri={encoded_return_url}&scope={__scope_str__}"

    return login_url


def is_login_azure_ok(request: Request):
    """
    If thy successful login to Microsoft Online.
    The fucking Microsoft online will redirect to return_url (the factor in   get_login_url)
    Nếu bạn đăng nhập thành công vào Microsoft Online.
    Microsoft trực tuyến chết tiệt sẽ chuyển hướng đến return_url (yếu tố trong get_login_url)
    :param request:
    :return:
    """
    if request.query_params.get("code"):
        return True
    else:
        return False


def get_verify_code(request: Request):
    """
    After successful login to Microsoft Online.
    The fucking Microsoft online will redirect to return_url (the factor in   get_login_url)
    In the fucking handle of return_url call this function. That fucking preparation to call get_access_token
    Sau khi đăng nhập thành công vào Microsoft Online.
    Microsoft trực tuyến chết tiệt sẽ chuyển hướng đến return_url (yếu tố trong get_login_url)
    Trong phần xử lý return_url, hãy gọi hàm này. Đó là sự chuẩn bị chết tiệt để gọi get_access_token
    :param request:
    :return:
    """
    return request.query_params.get("code")


def get_auth_token(verify_code, redirect_uri,tenant,client_id,client_secret)->AzureTokeResultInfo:
    """
    After get verify code.
    Call this fucking shit to get access token key
    Sau khi nhận được mã xác minh.
    Gọi cái thứ chết tiệt này để lấy chìa khóa mã thông báo truy cập
    :param verify_code:
    :param host_url:
    :param tenant:
    :param client_id:
    :param client_secret:
    :return:
    """

    grant_type = "authorization_code"
    data = {
        "grant_type": grant_type,
        "code": verify_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri

        # "scope": "https%3A%2F%2Fgraph.microsoft.com%2Fmail.read",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    #https://login.microsoftonline.com/13a53f39-4b4d-4268-8c5e-ae6260178923/oauth2/v2.0/token
    response = requests.post(f"https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        ret_info = AzureTokeResultInfo()
        for k,v in response_data.items():
            ret_info.__dict__[k]=v
        return ret_info
    else:
        re_json = response.json()
        from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
        if re_json.get("error"):
            raise FuckingWhoreMSApiCallException(
                code=re_json.get("error"),
                message=re_json.get("error_description")
            )
        raise Exception(f"Error: {response.status_code} {response.text}")
#sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout fs.key -out fs.crt
#