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
def upload_file(file_path:str,token:str):


    if not os.path.isfile(file_path):
        raise FileNotFoundError()
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file_path)[1]
    if file_ext!="":
        file_name = f"{file_id}{file_ext}"
    else:
        file_name = f"{file_id}"
    url = f'me/drive/root:/{file_name}:/content'

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