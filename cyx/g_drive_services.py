import os.path
import pathlib
import typing

import fastapi
import requests
from pydrive.auth import GoogleAuth
import google_auth_oauthlib.flow
import urllib3.util
import urllib.parse

import cy_docs
import cy_kit
from cyx.common import config
from cyx.repository import Repository
from cyx.cache_service.memcache_service import MemcacheServices
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import hashlib
from google.oauth2 import service_account

class GDriveService:
    def __init__(self, memcache_service=cy_kit.singleton(MemcacheServices)):
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.memcache_service = memcache_service
        self.cache_key_of_refresh_token = f"{type(self).__module__}_{type(self).__name__}"
        # self.gauth.settings['client_config_backend']='settings'

    def do_auth(self, client_id: str, client_secret: str, redirect_uri):

        self.gauth.LocalWebserverAuth()

    def get_login_url(self, request: fastapi.Request, app_name, client_id) -> object:

        """

        :return:
        """

        redirect_uri = f'https://{request.url.hostname}/' + request.url.path.split('/')[
            1] + '/api/' + app_name + '/after-google-login'
        url_parse = [
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
        authorization_url = "https://accounts.google.com/o/oauth2/auth?" + "&".join(url_parse)

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

    def get_access_token(self, code, client_id, client_secret):
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

    def get_id_and_secret(self, app_name) -> typing.Tuple[str | None, str | None]:
        qr = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name == app_name
        ).project(
            cy_docs.fields.ClientId >> Repository.apps.fields.AppOnCloud.Google.ClientId,
            cy_docs.fields.ClientSecret >> Repository.apps.fields.AppOnCloud.Google.ClientSecret
        )
        data = list(qr)
        if len(data) == 0:
            return None, None
        else:
            data = data[0]
            return data.get("ClientId"), data.get("ClientSecret")

    def save_refresh_access_token(self, app_name, refresh_token):
        Repository.apps.app("admin").context.update(
            Repository.apps.fields.Name == app_name,
            Repository.apps.fields.AppOnCloud.Google.RefreshToken << refresh_token

        )
        self.memcache_service.set_str(
            key=f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token",
            value=refresh_token
        )
        root_dir= self.get_root_folder(app_name)
        print(root_dir)

    def get_refresh_access_token(self, app_name):
        ret = self.memcache_service.get_str(f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token")
        if not ret:
            qr = Repository.apps.app("admin").context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.refresh_token >> Repository.apps.fields.AppOnCloud.Google.RefreshToken
            )
            data = list(qr)
            if len(data) == 0:
                return None
            else:
                refresh_token = data[0].refresh_token
                self.memcache_service.set_str(
                    key=f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token",
                    value=refresh_token
                )
                return refresh_token
        else:
            return ret

    def create_folder(self, app_name, folder_name: str):
        service = build('drive', 'v3', http=self.get_refresh_access_token(app_name))
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        client_id,client_secret = self.get_id_and_secret(app_name)
        from google.oauth2.credentials import Credentials as OAuth2Credentials
        credentials = OAuth2Credentials(
            token=self.get_refresh_access_token(app_name),
            refresh_token = self.get_refresh_access_token(app_name),
            token_uri = "https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        service = build('drive', 'v3', credentials=credentials)
        try:
            folder = service.files().create(body=file_metadata).execute()
            print(f"Folder created: {folder.get('id')}")
            return folder
        except Exception as ex:
            raise ex


    def get_root_folder(self, app_name):
        ret = self.memcache_service.get_str(f"{self.cache_key_of_refresh_token}_{app_name}_root_folder")
        if not ret:
            qr = Repository.apps.app('admin').context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.RootDir >> Repository.apps.fields.AppOnCloud.Google.RootDir
            )
            data = list(qr)
            if len(data) == 0:
                ret = None
            else:
                ret = data[0].RootDir
            if ret is None:
                ret = hashlib.sha256(app_name.encode()).hexdigest()
                Repository.apps.app('admin').context.update(
                    Repository.apps.fields.Name == app_name,
                    Repository.apps.fields.AppOnCloud.Google.RootDir << ret
                )
            self.memcache_service.set_str(f"{self.cache_key_of_refresh_token}_{app_name}_root_folder", ret)
        self.create_folder(app_name, ret)
        return ret
