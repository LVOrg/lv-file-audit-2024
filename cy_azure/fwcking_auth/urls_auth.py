import typing
import urllib.parse


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
