import typing
import urllib.parse
import requests
import json


def get_access_token_key_by_username_pass(
        client_id: str,
        username: str, password: str,
        scopes: typing.List[str],
        secret_value: str) -> typing.Optional[typing.Tuple[str, typing.List[str]]]:
    fucking_scope = list(set(scopes + ['offline_access', 'openid', 'profile'] + [f"api://{client_id}/all"]))
    txt_scope = "+".join(fucking_scope)
    data = {'grant_type': "password",  # "password", # "client_credentials",
            'resource': "https://graph.microsoft.com",
            # "https://graph.microsoft.com", # "553ae3ba-037a-4fc4-bd8e-368b06692c06" , # ["553ae3ba-037a-4fc4-bd8e-368b06692c06","https://graph.microsoft.com"],
            'client_id': client_id,
            'client_secret': secret_value,
            'scope': scopes + [
                'offline_access',
                'openid',
                'profile',
                'https://graph.microsoft.com/mail.read',
                'https://graph.microsoft.com/user.read.all',
                'https://graph.microsoft.com/user.ReadWrite.all',
                'https://graph.microsoft.com/Files.Read',
                'https://graph.microsoft.com/Files.Read.All',
                'https://graph.microsoft.com/Files.Read.Selected',
                'https://graph.microsoft.com/Files.ReadWrite',
                'https://graph.microsoft.com/Files.ReadWrite.All'
            ],
            'username': username,
            'password': password
            }

    URL3 = f"https://login.windows.net/common/oauth2/token"
    r = requests.post(url=URL3, data=data)
    print(r.text)
    j = json.loads(r.text)
    if j.get("error"):
        from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
        ex = FuckingWhoreMSApiCallException(
            code=j.get('error'),
            message=j['error_description']
        )
        raise ex
    TOKEN = j["access_token"]
    ret_scope = j["scope"].split(' ')
    return TOKEN, ret_scope


def accquire_access_token_key_token(
        client_id: str, tenant_id: str,
        secret_value: str) -> str:
    from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
    fucking_data_2 = {'grant_type': "client_credentials",  # "client_credentials",
                      # 'resource': "https://graph.microsoft.com",
                      'client_id': client_id,
                      'client_secret': secret_value,
                      'scope': ['https://graph.microsoft.com/.default'],
                      }
    fucking_ur = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    # fucking_ur = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"

    r = requests.post(url=fucking_ur, data=fucking_data_2)
    j = json.loads(r.text)
    if j.get("error"):
        ex = FuckingWhoreMSApiCallException(
            code=j.get('error'),
            message=j['error_description']
        )

        raise ex
    ret_token = j["access_token"]

    return ret_token


def get_personal_account_login_url(client_id: str, scopes: typing.List[str], redirect_uri: str) -> str:
    """

    :return:
    """
    # https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=7da41e72-1a30-48ac-a62b-8394d83cb931&response_type=code&scope=Files.Read+Files.Read.All+Files.ReadWrite+Files.ReadWrite.All+User.Read+User.Read.All+User.ReadWrite+User.ReadWrite.All+offline_access+openid+profile&redirect_uri=https%3A%2F%2F172.16.13.72%3A8012%2Flvfile%2Fapi%2Flv-docs%2Fazure%2Fafter_login
    fucking_scope = list(set(scopes + ['offline_access', 'openid', 'profile']))
    txt_scope = "+".join(fucking_scope)
    fucking_redirect_uri = urllib.parse.quote_plus(redirect_uri)
    fucking_url = (f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
                   f"client_id={client_id}"
                   f"&response_type=code"
                   f"&scope={txt_scope}&"
                   f"redirect_uri={fucking_redirect_uri}")
    return fucking_url


def get_business_account_login_url(client_id: str, tenant_id: str, scopes: typing.List[str], redirect_uri: str) -> str:
    fucking_scope = list(set(scopes + ['offline_access', 'openid', 'profile']))

    txt_scope = "+".join(fucking_scope)
    fucking_redirect_uri = urllib.parse.quote_plus(redirect_uri)
    fucking_url = (f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?"
                   f"client_id={client_id}&response_type=code&redirect_uri={fucking_redirect_uri}&scope={txt_scope}")
    return fucking_url
