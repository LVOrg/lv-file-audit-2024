import os.path
import pathlib
import typing

from gradio_client import Client
from cyx.common import config
import requests


class ThumbOfficeService:
    def __init__(self):
        self.server_thumb_office:str = config.server_thumb_office
        self.server_thumb_office=self.server_thumb_office.rstrip('/')+'/'
        self.client = Client(self.server_thumb_office)

    def generate_thumbs(self, file_path: str, output_dir: str, thumbs_constraint: str = "60,120,240,480,600,700") -> \
    typing.List[str]:
        # result = client.predict(
        #     "https://github.com/gradio-app/gradio/raw/main/test/test_files/sample_file.pdf",
        #     # filepath  in 'file_path' File component
        #     "Hello!!",  # str  in 'scale' Textbox component
        #     api_name="/predict"
        # )
        if not os.path.isfile(file_path):
            raise Exception(f"{file_path} was not found")
        url_images = self.client.predict(
            file_path, thumbs_constraint,
            api_name="/predict"
        )
        urls = url_images.lstrip("['").rstrip("']").split("', '")
        ret = []
        for x in urls:
            server_file_path = x
            if "/file=" in server_file_path:
                x=x.split("/file=")[1]
            url_download = self.server_thumb_office+"/file="+x
            server_file_name = os.path.split(server_file_path)[1]
            os.makedirs(output_dir, exist_ok=True)
            client_file_path = os.path.join(output_dir, server_file_name)
            response = requests.get(url_download, stream=True)
            with open(client_file_path, "wb") as f:
                # Iterate over the response data chunks and write them to the file
                for chunk in response.iter_content(chunk_size=1024):  # Download in chunks
                    f.write(chunk)
            ret += [client_file_path]
        return ret

import cy_kit
svc= cy_kit.singleton(ThumbOfficeService)
ret = svc.generate_thumbs(
    file_path=f'/home/vmadmin/python/cy-py/app_services/data-test/codx collaboration_userguidelist-khanh editing .docx',
    output_dir=f"/home/vmadmin/python/cy-py/a-working/download"
)

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
