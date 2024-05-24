import datetime
import os.path
import pathlib
import threading
import typing
import json
import fastapi
import requests
import urllib.parse
import io
import cy_docs
import cy_kit
from cyx.common import config
from cyx.repository import Repository
from cyx.cache_service.memcache_service import MemcacheServices
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import hashlib
from google.oauth2 import service_account
from gradio_client import Client
import cy_utils
from cyx.processing_file_manager_services import ProcessManagerService
from cyx.local_api_services import LocalAPIService
from cyx.common import config
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import HttpRequest as gRequest
from googleapiclient.errors import HttpError
from fastapi import HTTPException

from cy_xdoc.services.files import FileServices
from cyx.repository import Repository
import requests
import mimetypes
from fastapi.responses import StreamingResponse


class GoogleSettingsInfo:
    refresh_token: str
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    client_secret: str
    email: str
    client_id:str

from cyx.cloud_cache_services import CloudCacheService
class GDriveService:
    def __init__(self,
                 memcache_service=cy_kit.singleton(MemcacheServices),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 file_services=cy_kit.singleton(FileServices),
                 cloud_cache_service: CloudCacheService = cy_kit.singleton(CloudCacheService)
                 ):
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.memcache_service = memcache_service
        self.cache_key_of_refresh_token = f"{type(self).__module__}_{type(self).__name__}"
        self.local_api_service = local_api_service
        self.file_services = file_services
        self.cache_key_of_id_and_secret = f"{type(self).__module__}/{type(self).__name__}/id_and_secret"
        self.cloud_cache_service=cloud_cache_service
        # self.gauth.settings['client_config_backend']='settings'

    def do_auth(self, client_id: str, client_secret: str, redirect_uri):

        self.gauth.LocalWebserverAuth()

    def get_login_url(self, request: fastapi.Request, app_name, scopes: typing.List[str]) -> typing.Tuple[
        str | None, dict | None]:

        """

        :return:
        """
        client_id, client_secret, _, error = self.get_id_and_secret(app_name,from_cache=False)
        if client_id=="195042738785-dvqhu9vrm99d4c34umu7p1ggtm8f4csv.apps.googleusercontent.com":
            print("OK")
        if client_secret=="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":
            print("OK")
        if error:
            return None, error
        redirect_uri = f'https://{request.url.hostname}/' + request.url.path.split('/')[
            1] + '/api/' + app_name + '/after-google-login'
        full_scopes = [urllib.parse.quote_plus(f"https://www.googleapis.com/auth/{x}") for x in scopes]+["openid","email"]
        url_parse = [
            f"response_type=code",
            f"client_id={client_id}",
            f"redirect_uri={urllib.parse.quote_plus(redirect_uri)}",
            f"scope={' '.join(full_scopes)}",
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
        return authorization_url, None

    def get_access_token(self, code, client_id, client_secret, redirect_uri):

        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }

        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        response.raise_for_status()  # Raise exception for non-2xx status codes

        return response.json()

    def get_redirect_uri(self, app_name):
        qr = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name == app_name
        ).project(
            cy_docs.fields.RedirectUri >> Repository.apps.fields.AppOnCloud.Google.RedirectUri
        )
        data = list(qr)
        if len(data) == 0:
            return None
        else:
            return data[0].RedirectUri

    def resset_id_and_secret(self, app_name):
        self.memcache_service.delete_key(f"{self.cache_key_of_id_and_secret}/{app_name}")

    def get_id_and_secret(self, app_name, from_cache: bool = True) -> typing.Tuple[
        str | None, str | None, str | None, dict | None]:
        """
        Get ClientId, ClientSecret, Email and error
        :param app_name:
        :return: client_id, client_secret, email , error
        """
        ret_dict = None
        if from_cache:
            ret_dict = self.memcache_service.get_dict(f"{self.cache_key_of_id_and_secret}/{app_name}")
            if ret_dict and ret_dict.get("ClientId") and ret_dict.get("ClientSecret") and ret_dict.get("Email"):
                return ret_dict["ClientId"], ret_dict["ClientSecret"], ret_dict["Email"], None
        data = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name == app_name
        ).project(
            cy_docs.fields.ClientId >> Repository.apps.fields.AppOnCloud.Google.ClientId,
            cy_docs.fields.ClientSecret >> Repository.apps.fields.AppOnCloud.Google.ClientSecret,
            cy_docs.fields.Email >> Repository.apps.fields.AppOnCloud.Google.Email
        ).first_item()

        if data is None or data.ClientSecret is None:
            return None, None, None, dict(Code="GoogleWasNotFound", Message=f"App '{app_name}' did not link to "
                                                                            f"Google API yet")
        else:
            self.memcache_service.set_dict(f"{self.cache_key_of_id_and_secret}/{app_name}", data.to_json_convertable(),
                                           expiration=60 * 60 * 365)
            return data.ClientId, data.ClientSecret, data.Email, None

    def save_refresh_access_token(self, app_name, refresh_token, access_token, expires_in, scope, token_type):
        reset_key = f"{type(self).__module__}/{type(self).__name__}/get_settings/{app_name}"
        self.memcache_service.delete_key(reset_key)
        if not isinstance(refresh_token, str):
            print("warning refresh_token mus be str")
            return
        self.resset_id_and_secret(app_name)
        Repository.apps.app("admin").context.update(
            Repository.apps.fields.Name == app_name,
            Repository.apps.fields.AppOnCloud.Google.RefreshToken << refresh_token,
            Repository.apps.fields.AppOnCloud.Google.AccessToken << access_token,
            Repository.apps.fields.AppOnCloud.Google.ExpiresIn << expires_in,
            Repository.apps.fields.AppOnCloud.Google.Scope << scope,
            Repository.apps.fields.AppOnCloud.Google.TokenType << token_type,

        )
        self.memcache_service.set_str(
            key=f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token",
            value=refresh_token
        )

    def get_refresh_access_token(self, app_name, from_cache: bool = True) -> typing.Tuple[str | None, dict | None]:
        ret = None
        if from_cache:
            ret = self.memcache_service.get_str(f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token")
        if not ret:
            data = Repository.apps.app("admin").context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.refresh_token >> Repository.apps.fields.AppOnCloud.Google.RefreshToken,
                cy_docs.fields.secret_client >> Repository.apps.fields.AppOnCloud.Google.ClientSecret

            ).first_item()

            if data is None or data.secret_client is None:
                return None, dict(Code="GoogleWasNotFound", Message=f"'Google do not bestow {app_name}")
            else:
                refresh_token = data.refresh_token
                self.memcache_service.set_str(
                    key=f"{self.cache_key_of_refresh_token}_{app_name}_refresh_token",
                    value=refresh_token
                )
                return refresh_token, None
        else:
            return ret, None

    def create_folder(self, app_name, folder_name: str) -> dict | None:
        service = build('drive', 'v3', http=self.get_refresh_access_token(app_name))
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        client_id, client_secret, _, error = self.get_id_and_secret(app_name)
        if error:
            return error
        from google.oauth2.credentials import Credentials as OAuth2Credentials
        refresh_token, error = self.get_refresh_access_token(app_name)
        if error:
            return error
        credentials = OAuth2Credentials(
            token=self.get_refresh_access_token(app_name),
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        service = build('drive', 'v3', credentials=credentials)
        try:
            folder = service.files().create(body=file_metadata).execute()
            print(f"Folder created: {folder.get('id')}")
            return folder
        except Exception as ex:
            return dict(
                Code="System",
                Message=repr(ex)
            )

    def get_root_folder(self, app_name) -> typing.Tuple[str | None, dict | None]:
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
        error = self.create_folder(app_name, ret)
        if error:
            return None, error
        return ret, None

    def sync_to_drive(self, app_name, upload_item) -> dict | None:
        download_url, rel_path, download_file, token, share_id = self.local_api_service.get_download_path(upload_item,
                                                                                                          app_name)

        def running():
            g_token, error = self.get_access_token_from_refresh_token(app_name)
            if error:
                Repository.cloud_file_sync.app(app_name=app_name).context.update(
                    Repository.cloud_file_sync.fields.UploadId == upload_item.Id,
                    Repository.cloud_file_sync.fields.IsError << True,
                    Repository.cloud_file_sync.fields.ErrorContent << json.dumps(error, indent=4)
                )

            full_path = os.path.join("/mnt/files", rel_path)
            client_id, secret_key, email, error = self.get_id_and_secret(app_name)
            process_services_host = config.process_services_host or "http://localhost"

            url_google_upload = upload_item.url_google_upload
            google_file_id = upload_item.google_file_id
            try:
                txt_json = json.dumps(dict(
                    token=g_token,
                    file_path=full_path,
                    app_name=app_name,
                    url_google_upload=url_google_upload,
                    google_file_id=google_file_id,
                    client_id=client_id,
                    secret_key=secret_key,
                    google_file_name=upload_item.FileName,
                    memcache_server=config.cache_server,
                    folder_id=upload_item.google_folder_id,

                    #config.cache_server

                ))
                print(txt_json)
                client = Client(f"{process_services_host}:1116/")
                result = client.predict(
                    txt_json,
                    api_name="/predict"
                )
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == upload_item.Id,
                    Repository.files.fields.CloudId << result

                )

                upload_item[Repository.files.fields.CloudId] = result
                self.file_services.cache_upload_register_set(upload_item.Id, upload_item)
                Repository.cloud_file_sync.app(app_name=app_name).context.delete(
                    Repository.cloud_file_sync.fields.UploadId == upload_item.Id
                )
                try:
                    os.remove(full_path)
                except:
                    pass
            except Exception as ex:
                Repository.cloud_file_sync.app(app_name=app_name).context.update(
                    Repository.cloud_file_sync.fields.UploadId == upload_item.Id,
                    Repository.cloud_file_sync.fields.IsError << True,
                    Repository.cloud_file_sync.fields.ErrorContent << repr(ex)
                )

        threading.Thread(target=running).start()

    def get_access_token_from_access_token(self, app_name, nocache=False) -> typing.Tuple[str | None, dict | None]:
        """
        get access token by using refresh token
        :param app_name:
        :return: access_token, erro
        """
        info, error = self.get_settings(app_name,nocache)
        if error:
            return None, error
        client_id, client_secret, _, error = self.get_id_and_secret(app_name,from_cache=not nocache)
        if error:
            return None, error
        body = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': info.access_token
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_uri = "https://oauth2.googleapis.com/token"
        response = requests.post(token_uri, headers=headers, data=body)
        data = response.json()
        access_token = data.get('access_token')
        return access_token, None

    def get_access_token_from_refresh_token(self, app_name, from_cache: bool = True) -> typing.Tuple[
        str | None, dict | None]:
        """
        get access token by using refresh token
        :param app_name:
        :return: access_token, erro
        """
        access_token = None
        key = f"{type(self).__module__}/{type(self).__name__}/{app_name}/get_access_token_from_refresh_token"
        if from_cache:
            data = self.memcache_service.get_dict(key)
            if isinstance(data, dict):
                if isinstance(data.get("expires_on"), datetime.datetime):
                    if (data.get("expires_on")-datetime.datetime.utcnow()).total_seconds() > 5:
                        return data.get("access_token"),None

        refresh_token, error = self.get_refresh_access_token(app_name, from_cache)
        if error:
            return None, error
        client_id, client_secret, _, error = self.get_id_and_secret(app_name, from_cache)
        if error:
            return None, error
        body = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_uri = "https://oauth2.googleapis.com/token"
        response = requests.post(token_uri, headers=headers, data=body)
        data = response.json()
        if data.get("error"):
            refresh_token_nocache, error = self.get_refresh_access_token(app_name, from_cache=False)
            if error:
                return None, error
            client_id_nocache, client_secret_nocache, _, error = self.get_id_and_secret(app_name, from_cache=False)
            if error:
                return None, error
            body = {
                'grant_type': 'refresh_token',
                'client_id': client_id_nocache,
                'client_secret': client_secret_nocache,
                'refresh_token': refresh_token_nocache
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            token_uri = "https://oauth2.googleapis.com/token"
            response = requests.post(token_uri, headers=headers, data=body)
            data = response.json()
            if data.get("error"):
                return None, dict(Code=data.get("error"), Message=data.get("error_description"))
        access_token = data.get('access_token')
        expires_in = data.get("expires_in")
        expires_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        self.memcache_service.set_dict(key, dict(
            access_token=access_token,
            expires_on=expires_on
        ))

        return access_token, None

    def get_service(self, token, client_id, client_secret, g_service_name: str = "v3/drive") -> Resource:
        credentials = OAuth2Credentials(
            token=token,
            refresh_token=token,  # Assuming you have a refresh token (optional)
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )
        if not isinstance(g_service_name,str):
            return None
        version, service_name = tuple(g_service_name.split('/'))
        service = build(service_name, version, credentials=credentials)
        return service

    def get_service_by_token(self, app_name, token) -> typing.Tuple[Resource | None, dict | None]:
        client_id, client_secret, _, error = self.get_id_and_secret(app_name)
        if isinstance(error, dict):
            return None, error

        ret = self.get_service(
            token=token,
            client_id=client_id,
            client_secret=client_secret
        )
        return ret, None

    def get_service_by_app_name(self, app_name, g_service_name="v3/drive", from_cache: bool = True) -> typing.Tuple[
        Resource | None, dict | None]:
        """

        :param app_name:
        :param g_service_name: g_service_name is combination of Google service version and Google service name Example "v3/drive" or "v1/mail"
        :return:
        """
        # refresh_token = self.get_refresh_access_token(app_name)
        assert isinstance(g_service_name,str),"g_service_name must be str"

        # self.get_settings(app_name,nocache=not from_cache)
        # token, error = self.get_access_token_from_refresh_token(app_name)
        token, error = self.get_access_token_from_refresh_token(app_name, from_cache)
        if isinstance(error, dict):
            return None, error

        client_id, client_secret, _, error = self.get_id_and_secret(app_name, from_cache)
        if error:
            return None, error
        ret = self.get_service(
            token=token,
            client_id=client_id,
            client_secret=client_secret,
            g_service_name=g_service_name
        )
        # self.save_refresh_access_token(app_name,refresh_token)
        return ret, None

    def set_public_visibility(self, resource_id, service: Resource):
        # Replace with your credentials file path
        # Update permission to 'anyoneWithLink'
        permission = {'role': 'reader', 'type': 'anyoneWithLink'}

        try:
            service.files().permissions().create(fileId=resource_id, body=permission).execute()
            print(f"File visibility set to 'anyoneWithLink' for resource ID: {resource_id}")
        except HttpError as error:
            print(f"API error: {error}")

    def get_public_url(self, resource_id, token, client_id, client_secret):

        # Define the Drive API service
        service = self.get_service(
            token=token,
            client_id=client_id,
            client_secret=client_secret
        )

        # Get file details
        file_details = service.files().get(fileId=resource_id).execute()

        # Check if publicly shared
        if file_details.get('visibility') == 'anyoneWithLink':
            # Extract the public URL from webViewLink field (if available)
            public_url = file_details.get('webViewLink')
            if public_url:
                print(public_url)
                return public_url
            else:
                raise Exception("File is publicly shared but doesn't have a webViewLink")
        else:
            return None

    async def get_content_async(self,
                                app_name: str,
                                upload_id:str,
                                cloud_id: str,
                                client_file_name: str,
                                content_type:str,
                                request: fastapi.requests.Request,
                                nocache=False,
                                download_only=False) -> typing.Union[dict, StreamingResponse] | None:

        # url = f"https://drive.google.com/file/d/{cloud_id}/view?usp=drivesdk"
        if not nocache and not download_only:
            cache_file_path = self.cloud_cache_service.get_from_cache(upload_id)
            if cache_file_path:
                import cy_web
                fs = open(cache_file_path, "rb")

                def get_size():
                    return os.stat(cache_file_path).st_size

                setattr(fs, "get_size", get_size)
                ret = await cy_web.cy_web_x.streaming_async(
                    fs, request, content_type, streaming_buffering=1024 * 4 * 3 * 8
                )
                return ret
        content_type, _ = mimetypes.guess_type(client_file_name)
        uri = f"https://www.googleapis.com/drive/v3/files/{cloud_id}?alt=media"
        access_token, error = self.get_access_token_from_refresh_token(app_name)
        if isinstance(error, dict):
            raise HTTPException(status_code=505, detail=error)

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        if request.headers.get("range"):
            headers["range"] = request.headers["range"]
        response = requests.get(uri, headers=headers, stream=True)
        # response.headers["Content-Type"] = content_type
        # response.headers["Accept-Ranges"] = "bytes"

        # response.headers["Content-Range"] = request.headers.get('range')
        if response.headers.get("Content-Disposition") and not download_only:
            del response.headers['Content-Disposition']
        if response.headers.get("Content-Encoding"):
            del response.headers["Content-Encoding"]
        response.headers["Accept-Ranges"] = "bytes"
        # Return StreamingResponse object

        if content_type.startswith("image/"):
            self.cloud_cache_service.cache_content(app_name=app_name, upload_id=upload_id, url=uri,
                                                   cloud_id=cloud_id, header=headers)
        return StreamingResponse(
            content=response.iter_content(chunk_size=1024 * 4),
            headers=response.headers,
            media_type=content_type,
            status_code=response.status_code
        )

    def get_settings(self, app_name,nocache=False) -> typing.Tuple[GoogleSettingsInfo | None, dict | None]:
        key = f"{type(self).__module__}/{type(self).__name__}/get_settings/{app_name}"
        if not nocache:
            ret = self.memcache_service.get_object(key, GoogleSettingsInfo)
            if ret:
                return ret, None
        ret = GoogleSettingsInfo()
        data_item = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name == app_name
        ).project(
            cy_docs.fields.refresh_token >> Repository.apps.fields.AppOnCloud.Google.RefreshToken,
            cy_docs.fields.access_token >> Repository.apps.fields.AppOnCloud.Google.AccessToken,
            cy_docs.fields.expires_in >> Repository.apps.fields.AppOnCloud.Google.ExpiresIn,
            cy_docs.fields.scope >> Repository.apps.fields.AppOnCloud.Google.Scope,
            cy_docs.fields.token_type >> Repository.apps.fields.AppOnCloud.Google.TokenType,
            cy_docs.fields.client_secret >> Repository.apps.fields.AppOnCloud.Google.ClientSecret,
            cy_docs.fields.email >> Repository.apps.fields.AppOnCloud.Google.Email,
            cy_docs.fields.client_id >> Repository.apps.fields.AppOnCloud.Google.ClientId,

        ).first_item()
        if not data_item:
            return None, dict(Code="GoogleLinkIsNotReady", Message=f"Google did not bestow {app_name}")
        elif data_item.get("client_secret") is None:
            return None, dict(Code="GoogleLinkIsNotReady", Message=f"Google did not bestow {app_name}")
        for k, v in data_item.items():
            setattr(ret, k, v)
        self.memcache_service.set_object(key, ret)
        return ret, None


    def get_user_info(self,app_name:str):


        token, error =self.get_refresh_access_token(app_name=app_name)
        headers = {"Authorization": f"Bearer {token}"}
        user_info_url = "https://openidconnect.googleapis.com/v1/userinfo"
        res= requests.get(user_info_url, headers=headers)
        info,error=self.get_settings(app_name)
        if error:
            return error
        REFRESH_TOKEN = info.refresh_token
        CLIENT_ID = info.client_id
        CLIENT_SECRET = info.client_secret  # Keep this confidential!

        # Step 1: Get a new access token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN
        }

        response = requests.post(token_url, data=data)

        if response.status_code == 200:
            access_token = response.json()["access_token"]

            # Step 2: Access user info using the access token
            user_info_url = "https://openidconnect.googleapis.com/userinfo/v2/me"  # Example endpoint
            headers = {"Authorization": f"Bearer {info.access_token}"}

            user_info_response = requests.get(user_info_url, headers=headers)

            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                print(f"User Info: {user_info}")
            else:
                print(f"Error retrieving user info: {user_info_response.text}")
        else:
            print(f"Error getting access token: {response.text}")
