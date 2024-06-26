import time

from cyx.common import config
import asyncio
import aiohttp
from cyx.common import config
import requests
import aiohttp.client_exceptions

class FileUtilService:
    def __init__(self):
        self.content_service = config.content_service

    def healthz(self):
        def check():
            try:
                print(f"call {self.content_service}/healthz")
                response = requests.get(f"{self.content_service}/healthz")
                response.raise_for_status()  # Raise an exception for non-200 status codes

                # Process successful response
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")
            except:
                print(f"call {self.content_service}/api/healthz was fail")
                return False
            return True

        ok = check()
        while not ok:
            time.sleep(1)
            ok = check()

    async def call_api_async(self, api_path: str, data=None, headers=None)->dict:
        """Makes an asynchronous POST request to the given URL.

        Args:
            url (str): The URL of the endpoint to send the request to.
            data (dict, optional): The data to send in the request body. Defaults to None.
            headers (dict, optional): Additional headers to include in the request. Defaults to None.

        Returns:
            aiohttp.ClientResponse: The response object from the server.
            :param api_path:
        """
        url = f"{self.content_service}/{api_path}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    return await response.json()  # Parse the JSON response
        except aiohttp.client_exceptions.ClientResponseError as ex:
            return dict(
                Error=dict(
                    Message=f"{ex.message}\n{self.content_service}/{api_path}",
                    Code = "RemoteAPICallError"
                )
            )

    async def register_new_upload_local_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/local"
        )
        return ret

    async def register_new_upload_google_drive_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/google-drive"
        )
        return ret

    async def register_new_upload_one_drive_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/register/one-drive"
        )
        return ret

    async def update_upload_local_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/local/one-drive"
        )
        return ret

    async def update_google_drive_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/update/google-drive"
        )
        return ret

    async def update_upload_one_drive_async(self, app_name,from_host, data):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                data=data,
            ),
            api_path="files/update/one-drive"
        )
        return ret

    async def push_file_async(self, app_name, from_host, file_path, index, upload_id):
        ret = await self.call_api_async(
            data=dict(
                app_name=app_name,
                from_host=from_host,
                file_path=file_path,
                index=index,
                upload_id=upload_id
            ),
            api_path="files/push-file"
        )
        return ret
