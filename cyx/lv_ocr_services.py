from cyx.common import config
import requests

class LVOCRService:
    def __init__(self):
        self.url = config.ocr_api
        self.token = config.ocr_token


    def do_orc(self, file_path):
        headers = {
            "Api_key": self.token,
            'Api-Version':"1.0"
        }
        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            response = requests.post(self.url,headers=headers, files=files)

            response.raise_for_status()  # Raise an exception if the request fails

            data = response.json()
            return data.get('Data',{}).get('Content','')
