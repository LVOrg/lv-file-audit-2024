import json
import os
import typing
import uuid

import pathlib

from cyx.common import config

import requests

from cyx.repository import Repository


class LocalAPIService:
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
        jwt_secret_key= config.jwt.secret_key
        algorithm = config.jwt.algorithm
        username=config.jwt.secret_user
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
                  file_path: str, token: str | None,
                  local_share_id: str | None,
                  app_name: str | None,
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

    def get_download_path(self, upload_item, app_name) -> typing.Tuple[ str | None, str | None, str | None, str | None, str | None]:
        """
        Get all info of server_file, rel_file_path, download_file_path, token, local_share_id
        :param upload_item:
        :param app_name:
        :return: server_file, rel_file_path, download_file_path, token, local_share_id
        """
        rel_file_path = None
        server_file, rel_file_path, download_file_path, token, local_share_id = None, None, None, None, None
        try:
            rel_file_path: str = upload_item["MainFileId"].split("://")[1]
            file_ext = pathlib.Path(rel_file_path).suffix
        except:
            file_name = upload_item[Repository.files.fields.FileName].lower()
            file_ext = pathlib.Path(file_name).suffix
            download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
            server_file = config.private_web_api +f"/api/{app_name}/file/{upload_item.id}"
            return server_file, rel_file_path, download_file_path, token, local_share_id
        print(f"process file {rel_file_path} ...")
        local_share_id = None
        token = None
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
