import threading

import requests
from cyx.common import config
class RemoteCallerService:
    def __init__(self):
        pass

    def get_image_from_office(self, url_of_office_to_image_service:str, url_of_content:str, url_upload_file:str):
        """
        :param url_of_office_to_image_service:
        :param url_of_content:
        :param url_upload_file:
        :return:
        """

        try:
            response = requests.post(url_of_office_to_image_service + "/get-image", json=dict(
                url_of_content=url_of_content,
                url_upload_file=url_upload_file
            ))
            response.raise_for_status()
            return response.json()
        except:
            raise Exception(f"remote call error {url_of_content}\n{response.text}")

    def get_thumb(self, url_of_thumb_service:str, url_of_image:str, url_upload_file:str, size: int):
        """

        :param size: Thumb size
        :param url_of_thumb_service: url of service process thumb
        :param url_of_image: url of image
        :param url_upload_file: url upload thumb file after process thumb
        :return:
        """

        try:
            response = requests.post(url_of_thumb_service + "/get-thumb", json=dict(
                size=size,
                url_of_thumb_service=f'{url_of_thumb_service}/get-thumb',
                url_of_image=url_of_image,
                url_upload_file=url_upload_file
            ))
            response.raise_for_status()
            return response.json()
        except:
            raise Exception(f"remote call error {url_of_thumb_service}\n{response.text}")

    def get_image_from_pdf(self, download_url, upload_url):
        uri:str = f'{config.remote_pdf}/get-image'

        try:
            response = requests.post(uri, json=dict(
                download_url=download_url,
                upload_url=upload_url
            ))
            response.raise_for_status()
            return response.json()
        except:
            raise Exception(f"remote call error {uri}\n{response.text}")

    def get_image_from_video(self, download_url, upload_url):
        uri: str = f'{config.remote_video}/get-image'

        try:
            response = requests.post(uri, json=dict(
                download_url=download_url,
                upload_url=upload_url
            ))
            response.raise_for_status()
            return response.json()
        except:
            raise Exception(f"remote call error {uri}\n{response.text}")