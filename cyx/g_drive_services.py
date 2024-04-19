import os.path
import pathlib

import fastapi
import requests
from pydrive.auth import GoogleAuth
import google_auth_oauthlib.flow
import urllib3.util
import urllib.parse
from cyx.common import config
class GDriveService:
    def __init__(self):
        self.gauth = GoogleAuth(settings_file=f"/home/vmadmin/python/cy-py/google.yml")
        self.gauth.settings["refresh_token"]="true"
        self.gauth.settings['client_config_file']=f"/home/vmadmin/python/cy-py/client_secrets.json"
        self.working_dir= pathlib.Path(__file__).parent.parent.__str__()
        # self.gauth.settings['client_config_backend']='settings'


    def do_auth(self, client_id:str,client_secret:str,redirect_uri):

        self.gauth.LocalWebserverAuth()

    def get_login_url(self,request:fastapi.Request,app_name,client_id) -> object:

        """

        :return:
        """

        redirect_uri=f'https://{request.url.hostname}/'+request.url.path.split('/')[1]+'/api/'+app_name+'/after-google-login'
        url_parse=[
            f"response_type=code",
            f"client_id={client_id}",
            f"redirect_uri={urllib.parse.quote_plus(redirect_uri)}",
            f"scope={urllib.parse.quote_plus('https://www.googleapis.com/auth/drive')}",
            f"state=ok",
            f"access_type=offline",
            f"include_granted_scopes=true",
            f'login_hint=hint%40example.com',
            f"prompt=consent"

        ]
        authorization_url= "https://accounts.google.com/o/oauth2/auth?"+"&".join(url_parse)

        # flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        #     os.path.join(self.working_dir,"client_secrets.json"),
        #     scopes=['https://www.googleapis.com/auth/drive'],
        #     redirect_uri="https://docker.lacviet.vn/lvfile/api/lv-docs/after-google-login"
        # )
        #
        # authorization_url, state = flow.authorization_url(
        #     # Recommended, enable offline access so that you can refresh an access token without
        #     # re-prompting the user for permission. Recommended for web server apps.
        #     access_type='offline',
        #     # Optional, enable incremental authorization. Recommended as a best practice.
        #     include_granted_scopes='true',
        #     # Recommended, state value can increase your assurance that an incoming connection is the result
        #     # of an authentication request.
        #     state="ok",
        #     # Optional, if your application knows which user is trying to authenticate, it can use this
        #     # parameter to provide a hint to the Google Authentication Server.
        #     login_hint='hint@example.com',
        #     # Optional, set prompt to 'consent' will prompt the user for consent
        #     prompt='consent'
        #
        # )
        # fx=urllib3.util.parse_url(authorization_url)
        return authorization_url

    def get_access_token(self, code,client_id,client_secret):
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": "https://docker.lacviet.vn/lvfile/api/lv-docs/after-google-login"
        }

        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        response.raise_for_status()  # Raise exception for non-2xx status codes

        return response.json()

