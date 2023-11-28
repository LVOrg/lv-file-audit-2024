import typing

import msal


class MSAppService:
    def __init__(self):
        self.apps_cache = {}

    def get_ms_app(self,
                   client_id: str,
                   authority: typing.Optional[str] = "https://login.microsoftonline.com/common") -> typing.Optional[
        msal.PublicClientApplication]:
        """
        In order to work with fucking whore Microsoft. Call this fucking shit function to create an app
        :param client_id:
        :return:
        """
        cache_key = f"{client_id}/{authority or 'all'}"
        if not self.apps_cache.get(cache_key):

            ret = msal.PublicClientApplication(
                client_id=client_id,
                authority=authority
            )
            self.apps_cache[cache_key] = ret
        return self.apps_cache[cache_key]

    def get_url_login(self, client_id: str):
        app = self.get_ms_app(client_id)
        app.acquire_token_by_auth_code_flow()

    def get_login_url(self,
                      client_id: str,
                      redirect_uri: str,
                      scopes: typing.List[typing.AnyStr]=["https://graph.microsoft.com/user.read"]
                      ) -> typing.Optional[str]:
        """
        In order to work with Microsoft-Online the first fucking step create and get auth_code.
        That fucking shit will help thy get access token and refresh access token.
        :param scopes:
        :param redirect_uri:
        :return:
        """

        __scope__ = [
            'openid',
            'offline_access'
        ]

        __scope__+= scopes
        app = self.get_ms_app(client_id=client_id)
        auth_code_flow = app.initiate_auth_code_flow(scopes=__scope__, redirect_uri=redirect_uri)
        authorization_url = auth_code_flow["auth_uri"]
        return authorization_url
