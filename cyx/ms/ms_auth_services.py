import datetime
import typing
import json
import requests
import msal
import jwt
from urllib import parse


class MSAuthService:
    def __init__(self):
        pass

    def get_access_token_and_roles(self, tenant_id: str, client_id: str, client_secret: str) -> typing.Tuple[
        str, typing.List[str]]:
        url = f'https://login.microsoftonline.com/{tenant_id}'
        app = msal.ConfidentialClientApplication(
            client_id, authority=url,
            client_credential=client_secret)
        ret = app.acquire_token_for_client(scopes=[
            "https://graph.microsoft.com/.default"
        ])
        if ret.get("error_description"):
            raise Exception(ret.get("error_description"))
        token = ret.get('access_token')
        payload = jwt.decode(token, verify=False)
        return ret.get('access_token'), payload.get("roles") or []
    def get_url_login(self, tenant_id: str, client_id: str, redirect_uri: str, scopes: typing.List[str]):

        #"openid offline_access https://graph.microsoft.com/user.read"
        txt_scope = " ".join([x.lower() for x in scopes] + ["offline_access","openid"])

        url_format = (f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
                      f"client_id={client_id}&"
                      f"response_type=code&"
                      f"redirect_uri={parse.quote_plus(redirect_uri)}&"
                      f"response_mode=query&"
                      f"scope={parse.quote_plus(txt_scope)}&"
                      f"state=12345")
        return url_format

    def get_access_token_from_code(self,client_id: str, redirect_uri: str, scopes: typing.List[str],code:str,client_serect:str):
        txt_scope = " ".join(scopes + ["offline_access"])
        data = {
            "client_id": client_id,
            "scope": txt_scope,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "client_secret": client_serect  # Consider using environment variables or secure storage for client secret
        }

        # Set headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Send POST request to the Microsoft login endpoint
        url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
        response = requests.post(url, headers=headers, data=data)

        # Check for successful response
        if response.status_code == 200:
            # Parse the JSON response to get access token
            response_data = response.json()
            access_token = response_data["access_token"]
            return access_token

    def get_access_token_from_refresh_token(self,
                                            client_id: str,
                                            client_secret: str,
                                            tenant_id: str,
                                            refresh_token: str,
                                            redirect_uri: str,
                                            scope: str
                                            )->typing.Tuple[str|None,datetime.datetime|None,dict|None]:
        """
        Obtains a new access token using a refresh token for Microsoft Graph API.

        Args:
            client_id: Client ID (App ID) of your Azure AD application.
            client_secret: Client Secret of your Azure AD application.
            tenant_id: Tenant ID (Directory ID) of your Azure AD application.
            refresh_token: Refresh token obtained during the initial authentication flow.

        Returns:
            access_token and expires_in in second, dict of error if has error else error is Non
        """

        # Microsoft token endpoint URL
        token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"

        # Request body parameters
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "redirect_uri":redirect_uri,
            "scope":scope
        }

        # Send POST request to token endpoint
        response = requests.post(token_url, data=data)

        # Check for successful response
        response_data = response.json()

        if response_data.get('error'):
            return None,None,dict(error=response_data.get('error'),description=response_data.get('error_description'))
        utc_expire = datetime.datetime.utcnow()+datetime.timedelta(seconds=int(response_data.get("expires_in")))
        return response_data.get("access_token"), utc_expire,None
    def get_token_info(self,access_token:str)->dict:
        payload = jwt.decode(access_token, verify=False)
        return payload

