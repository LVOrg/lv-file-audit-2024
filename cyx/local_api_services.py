import json
import uuid

from cyx.common import config

import requests

from cyx.repository import Repository


class LocalAPIService:
    def __init__(self):
        self.cache = {}
        self.private_web_api = config.private_web_api

    def get_access_token(self, username: str, password: str) -> str:
        if isinstance(self.cache.get(f"{username}/{password}"), str):
            return self.cache.get(f"{username}/{password}")
        else:
            url = f"{self.private_web_api}/api/accounts/token"
            data = {"username": username, "password": password}  # Replace with your form data

            # Send a POST request with form data
            response = requests.post(url, data=data)
            if response.status_code == 200:
                ret_data = json.loads(response.content.decode())
                if isinstance(ret_data.get("access_token"), str):
                    self.cache[f"{username}/{password}"] = ret_data.get("access_token")
                return self.cache.get(f"{username}/{password}")
            else:
                return None

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
        url=f"{config.private_web_api}/api/sys/admin/create-raw-content"
        if token:
            headers['Authorization']= f'Bearer {token}'

        try:
            response = requests.post(url, headers=headers, files=files,data={
                "rel_path":rel_server_path,
                "app_name":app_name,
                "local_share_id":local_share_id
            })
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Handle successful response (e.g., print status code)
            print(f"Image submission successful. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error submitting image: {e}")
