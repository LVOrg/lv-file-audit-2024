import json

from cyx.common import config

import requests


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
