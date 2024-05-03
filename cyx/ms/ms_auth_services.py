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
        return ret.get('access_token'), payload.get("roles")
    def get_url_login(self, tenant_id: str, client_id: str, redirect_uri: str, scopes: typing.List[str]):
        txt_scope = " ".join(scopes + ["offline_access"])

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
