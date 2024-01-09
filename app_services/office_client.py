import os.path
import pathlib
import threading
import typing

from gradio_client import Client

import cy_kit
from cyx.common import config
import requests
import httpx
import gradio_client.exceptions
from cyx.cache_service.memcache_service import MemcacheServices
from  cyx.common import config

class ThumbOfficeService:
    def __init__(self, memcache_services=cy_kit.singleton(MemcacheServices)):
        self.memcache_services = memcache_services
        self.server_thumb_office: str = config.server_thumb_office
        self.server_thumb_office = self.server_thumb_office.rstrip('/') + '/'
        self.client = Client(self.server_thumb_office)
        self.cache_key = f"{config.file_storage_path}/v2/{__file__}/{type(self).__name__}/__init__"
        self.data = self.memcache_services.set_dict(self.cache_key, {}, expiration=365 * 60 * 60)
        self.start = False

    def __generate_thumbs__(self,
                            file_path: str,
                            download_to_dir: str,
                            thumbs_constraint: str = "60,120,240,480,600,700") -> \
            typing.List[str]:
        if not os.path.isfile(file_path):
            raise Exception(f"{file_path} was not found")
        try:
            url_images = self.client.predict(
                file_path, thumbs_constraint,
                api_name="/predict"
            )
            url_images = url_images.replace(' ', '')
            urls = url_images.lstrip("['").rstrip("']").split("','")
            ret = []
            for x in urls:
                server_file_path = x
                if "/file=" in server_file_path:
                    x = x.split("/file=")[1]
                url_download = self.server_thumb_office + "file=" + x
                server_file_name = os.path.split(server_file_path)[1]
                os.makedirs(download_to_dir, exist_ok=True)
                client_file_path = os.path.join(download_to_dir, server_file_name)
                response = requests.get(url_download, stream=True)
                with open(client_file_path, "wb") as f:
                    # Iterate over the response data chunks and write them to the file
                    for chunk in response.iter_content(chunk_size=1024):  # Download in chunks
                        f.write(chunk)
                ret += [client_file_path]
            return ret
        except:
            return []

    def generate_thumbs(self,
                        file_path: str,
                        download_to_dir: str,
                        thumbs_constraint: str = "60,120,240,480,600,700") -> \
            typing.List[str]:
        def start_run():
            self.data = self.memcache_services.get_dict(self.cache_key) or {}
            while True:
                keys = list(self.data.keys())
                if len(keys) > 0:
                    key = keys[0]
                    value = self.data[key]

                    self.memcache_services.set_dict(self.cache_key, self.data)
                    self.__generate_thumbs__(
                        file_path=value["file_path"],
                        download_to_dir=value['download_to_dir'],
                        thumbs_constraint=value['thumbs_constraint']
                    )
                    if self.data.get(key):
                        del self.data[key]

        th = threading.Thread(target=start_run)
        th.start()
        self.data = self.memcache_services.get_dict(self.cache_key) or {}
        if self.data.get(file_path) is None:
            self.data[file_path]=dict(
                file_path=file_path,
                download_to_dir=download_to_dir,
                thumbs_constraint=thumbs_constraint
            )
            self.memcache_services.set_dict(self.cache_key,self.data) or {}

# import cy_kit
# svc= cy_kit.singleton(ThumbOfficeService)
# ret = svc.generate_thumbs(
#     file_path=f'/home/vmadmin/python/cy-py/app_services/data-test/codx collaboration_userguidelist-khanh editing .docx',
#     output_dir=f"/home/vmadmin/python/cy-py/a-working/download"
# )
# ret = svc.generate_thumbs(
#     file_path=f'/home/vmadmin/python/cy-py/app_services/data-test/codx collaboration_userguidelist-khanh editing .docx',
#     output_dir=f"/home/vmadmin/python/cy-py/a-working/download"
# )
# ret = svc.generate_thumbs(
#     file_path=f'/home/vmadmin/python/cy-py/app_services/data-test/codx collaboration_userguidelist-khanh editing .docx',
#     output_dir=f"/home/vmadmin/python/cy-py/a-working/download"
# )


# office_server_url = "http://172.16.13.72:8014"
# office_server_url = "http://172.16.7.99:31792"
# file_test = f'/home/vmadmin/python/cy-py/cy_external_server/data-test/codx collaboration_userguidelist-khanh editing .docx'
# client = Client(office_server_url)
# url_image = client.predict(
#     file_test,  # filepath  in 'name' File component
#     api_name="/predict"
# )
# url_download = f"{office_server_url}/file={url_image}"
# import requests
#
# # Specify the URL of the file to download
#
# response = requests.get(url_download, stream=True)  # Stream the response to avoid memory issues
#
# # Check for successful response
# if response.status_code == 200:
#     # Open a local file in binary write mode
#     with open(filename, "wb") as f:
#         # Iterate over the response data chunks and write them to the file
#         for chunk in response.iter_content(chunk_size=1024):  # Download in chunks
#             f.write(chunk)
#
#     print("File downloaded successfully!")
# else:
#     print("Error downloading file. Status code:", response.status_code)
#
# # http://172.16.13.72:8014/file=/tmp/gradio/795202e536ce60624722566649b47171ee1e8b64/result/codx collaboration_userguidelist-khanh editing  2.png
# print(result)
