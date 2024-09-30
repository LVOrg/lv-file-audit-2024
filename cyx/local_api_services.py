import functools
import hashlib
import json
import os
import typing
import uuid

import pathlib

import cy_kit
from cyx.common import config

import requests
import functools
if hasattr(functools,"cache"):
    from functools import cache as ft_cache

else:
    from functools import lru_cache


    def ft_cache(*args, **kwargs):
        return functools.lru_cache(maxsize=128)(*args, **kwargs)
from cyx.repository import Repository
from cyx.cache_service.memcache_service import MemcacheServices

from datetime import datetime
class LocalAPIService:
    memcache_services = cy_kit.singleton(MemcacheServices)

    def __init__(self):
        self.cache = {}
        self.private_web_api = config.private_web_api

    def create_access_token(self):
        from jose import JWTError, jwt
        """
        jwt:
          secret_key: 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
          algorithm: HS256
          access_token_expire_minutes: 480
        """
        jwt_secret_key = config.jwt.secret_key
        algorithm = config.jwt.algorithm
        username = config.jwt.secret_user
        payload = {
            "audience": username
        }

        encoded_token = jwt.encode(payload, jwt_secret_key, algorithm=algorithm)
        return encoded_token

    def get_access_token(self, username: str, password: str) -> str:
        return self.create_access_token()

    def generate_local_share_id(self, app_name: str, upload_id: str) -> str:
        context = Repository.doc_local_share_info.app(
            app_name=app_name
        )
        share_id = str(uuid.uuid4())
        context.context.insert_one(
            context.fields.UploadId << upload_id,
            context.fields.LocalShareId << share_id
        )
        return share_id

    def check_local_share_id(self, app_name: str, local_share_id: str):
        context = Repository.doc_local_share_info.app(
            app_name=app_name
        )
        ret = context.context.find_one(
            context.fields.LocalShareId == local_share_id
        )
        return ret

    def send_file(self,
                  file_path: str,
                  token: typing.Optional[str],
                  local_share_id: typing.Optional[str],
                  app_name: typing.Optional[str],
                  rel_server_path: str):
        """Submits an image to the specified URL using a POST request.

            Args:
                image_path (str): Path to the image file.
                url (str): The URL of the API endpoint.
            """

        with open(file_path, 'rb') as image_file:
            image_data = image_file.read()

        headers = {}
        files = {'content': (file_path, image_data, 'image/png')}  # Adjust content type if needed
        # /lvfile/api/sys/admin/content-share/{rel_path}
        url = f"{config.private_web_api}/api/sys/admin/content-share/{rel_server_path}"
        if token:
            url += f"?token={token}"
        elif local_share_id:
            url += f"?local-share-id={local_share_id}"

        try:
            response = requests.post(url, files=files)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Handle successful response (e.g., print status code)
            print(f"Image submission successful. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise e

    def get_download_path_by_upload_id(self, upload_id:str, app_name:str):
        key = self.get_cache_key(f"f{app_name}/{app_name}")
        ret_url = self.memcache_services.get_str(key)
        if ret_url:
            return ret_url
        upload_item = Repository.files.app(app_name).context.find_one(
            (Repository.files.fields.id == upload_id) & (Repository.files.fields.Status == 1)
        )
        if upload_item is None:
            return None


        server_file, _, _, _, _ = self.get_download_path(
            upload_item=upload_item,
            app_name=app_name
        )
        self.memcache_services.set_str(key,server_file)
        return server_file



    def get_download_path(self, upload_item:typing.Dict[str,typing.Any], app_name:str,
                          to_file_ext:typing.Optional[str]= None) -> typing.Tuple[
        typing.Optional[str],
        typing.Optional[str],
        typing.Optional[str],
        typing.Optional[str],
    typing.Optional[str]]:
        """
        Get all info of server_file, rel_file_path, download_file_path, token, local_share_id
        :param upload_item:
        :param app_name:
        :return: server_file, rel_file_path, download_file_path, token, local_share_id
        """

        server_file, rel_file_path, download_file_path, token, local_share_id = None, None, None, None, None
        try:
            rel_file_path: str = upload_item[Repository.files.fields.MainFileId.__name__].split("://")[1]
            if to_file_ext:
                rel_file_path = f'{rel_file_path}.{to_file_ext}'
            file_ext = pathlib.Path(rel_file_path).suffix
        except:
            file_name = upload_item[Repository.files.fields.FileName].lower()
            file_ext = pathlib.Path(file_name).suffix
            download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
            server_file = config.private_web_api + f"/api/{app_name}/file/{upload_item.id}"
            return server_file, rel_file_path, download_file_path, token, local_share_id
        print(f"process file {rel_file_path} ...")
        local_share_id = None
        token = None
        physical_file_path = os.path.join(config.file_storage_path, rel_file_path.replace('/',os.sep))
        if os.path.isfile(physical_file_path):
            server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        else:
            file_ext = upload_item.get(Repository.files.fields.FileExt.__name__)
            rel_dir_path = pathlib.Path(rel_file_path).parent.__str__()
            version = upload_item.get(Repository.files.fields.VersionNumber.__name__,1)

            if file_ext:
                rel_file_path_with_version = f'{rel_dir_path}/data.{file_ext.lower()}-version-{version}'
            else:
                rel_file_path_with_version = f'{rel_dir_path}/data.{file_ext.lower()}-version-{version}'
            physical_file_path_with_version = os.path.join(config.file_storage_path, rel_file_path_with_version.replace('/',os.sep))
            if os.path.isfile(physical_file_path_with_version):
                rel_file_path = rel_file_path_with_version
            server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        # es_server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path+".search.es"
        if not upload_item.get("local_share_id"):
            token = self.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = upload_item["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={app_name}"

        download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
        return server_file, rel_file_path, download_file_path, token, local_share_id

    @ft_cache
    def get_cache_key(self, local_key:str):
        ret = hashlib.sha256(f"v-02/{local_key}".encode()).hexdigest()
        return ret

    def get_upload_path_by_upload_id(self,
                                     upload_id,
                                     app_name,
                                     file_name: typing.Optional[str] = None,
                                     file_ext: typing.Optional[str] = None,) -> typing.Optional[str]:
        key = self.get_cache_key(f'{upload_id}/{app_name}/{(file_name or "default")+"."+(file_ext or "unknown")}')
        ret_url = self.memcache_services.get_str(key)
        if ret_url is None:
            upload_item = Repository.files.app(app_name).context.find_one(
                (Repository.files.fields.id==upload_id) & (Repository.files.fields.Status ==1)
            )
            if upload_item is None:
                return None
            ret_url = self.get_upload_path(upload_item,app_name,file_name,file_ext)
            self.memcache_services.set_str(key,ret_url)
        return ret_url

    def get_upload_path(self,
                        upload_item:typing.Dict[str,typing.Any],
                        app_name:str, file_name:typing.Optional[str]=None,
                        file_ext: typing.Optional[str]=None) -> str:
        """
        Get get_upload_path
        :param file_ext:
        :param file_name: if is None file_name is file_name in upload_item[Repository.files.fields.FileName]
        :param upload_item:
        :param app_name:
        :return: local_upload_uri
        """
        if file_name is None and file_ext is None:
            raise ValueError(f"file_name is None and file_ext is None")

        file_name = file_name or (upload_item.get(Repository.files.fields.FileName.__name__)+"."+file_ext)
        register_on:str|datetime = upload_item.get(Repository.files.fields.RegisterOn.__name__)
        if isinstance(register_on,datetime):
            register_dir = register_on.strftime("%Y/%m/%d")
        else:
            register_dir = datetime.fromisoformat(register_on).strftime("%Y/%m/%d")
        register_app_dir = f"{app_name}/{register_dir}"
        sub_dir = "unknown"
        file_ext_of_upload = upload_item.get(Repository.files.fields.FileExt.__name__)
        if file_ext_of_upload:
            sub_dir = file_ext_of_upload[0:3]

        server_file = f"{config.private_web_api}/api/sys/admin/content-write/{register_app_dir}/{sub_dir}/{upload_item.get('_id')}/{file_name}"
        if file_ext:
            server_file = f'{server_file}.{file_ext}'

        if not upload_item.get("local_share_id"):
            token = self.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = upload_item["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={app_name}"
        return server_file
