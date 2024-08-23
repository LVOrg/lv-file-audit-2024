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
        response = requests.post(url_of_office_to_image_service + "/get-image", json=dict(
            url_of_content=url_of_content,
            url_upload_file=url_upload_file
        ))
        try:
            return response.json()
        except:
            print(response.text)
            return dict(error=dict(Code="RemoteERR500", Description=response.text))

    def get_thumb(self, url_of_thumb_service:str, url_of_image:str, url_upload_file:str, size: int):
        """

        :param size: Thumb size
        :param url_of_thumb_service: url of service process thumb
        :param url_of_image: url of image
        :param url_upload_file: url upload thumb file after process thumb
        :return:
        """
        response = requests.post(url_of_thumb_service+"/get-thumb", json=dict(
            size=size,
            url_of_thumb_service = f'{url_of_thumb_service}/get-thumb',
            url_of_image = url_of_image,
            url_upload_file = url_upload_file
        ))
        try:
            return response.json()
        except:
            print(response.text)
            return dict(error=dict(Code="RemoteERR500",Description=response.text))

    def get_image_from_pdf(self, download_url, upload_url):
        uri:str = f'{config.remote_pdf}/get-image'
        def running():
            response = requests.post(uri , json=dict(
                download_url = download_url,
                upload_url = upload_url
            ))
            try:
                return response.json()
            except:
                print(response.text)
                return dict(error=dict(Code="RemoteERR500", Description=response.text))
        threading.Thread(target=running).start()

    def get_image_from_video(self, download_url, upload_url):
        uri: str = f'{config.remote_video}/get-image'

        def running():
            response = requests.post(uri, json=dict(
                download_url=download_url,
                upload_url=upload_url
            ))
            try:
                return response.json()
            except:
                print(response.text)
                return dict(error=dict(Code="RemoteERR500", Description=response.text))

        threading.Thread(target=running).start()