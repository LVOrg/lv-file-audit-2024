import urllib
class AzureRequest:
    def __init__(self,tenant_id:str,client_id:str):
        self.tenant_id = tenant_id
        self.client_id = client_id

    def get_login_url(self,return_url):
        """
        Get the login URL.

        Args:
          return_url: The return URL.

        Returns:
          The login URL.
        """

        scope = "openid offline_access https://graph.microsoft.com/user.read"
        ret_url = urllib.parse.quote_plus(return_url)
        login_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize?client_id={self.client_id}&response_type=code&redirect_uri={ret_url}&scope={scope}"

        return login_url