"""
The fucking package according on :
https://github.com/pranabdas/Access-OneDrive-via-Microsoft-Graph-Python/blob/main/README.md
"""
import uuid

from cy_azure.fwcking_ms.caller import call_ms_func
import requests
import json
import urllib
import os
from getpass import getpass
import time
from datetime import datetime
def upload_file(file_path:str,token:str,user_id:str="c311a7df-4b78-48bc-b403-0e7d13383c15"):


    if not os.path.isfile(file_path):
        raise FileNotFoundError()
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file_path)[1]
    if file_ext!="":
        file_name = f"{file_id}{file_ext}"
    else:
        file_name = f"{file_id}"
    #URL = "https://graph.microsoft.com/v1.0/users/YOURONEDRIVEUSERNAME/drive/root:/fotos/HouseHistory"
    #https://graph.microsoft.com/v1.0/users/c311a7df-4b78-48bc-b403-0e7d13383c15/drive/root
    url = f'users/{user_id}/drive/items/root:/{file_name}:/content'

    content = open(file_path, 'rb')
    ret = call_ms_func(
        method="put",
        api_url=url,
        body=content,
        return_type=dict,
        request_content_type=None,
        token=token
    )
    return ret
