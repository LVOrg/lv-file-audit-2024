#https://www.lieben.nu/liebensraum/2019/04/uploading-a-file-to-onedrive-for-business-with-python/
import typing

import requests
import json
import urllib
def get_access_token_key(client_id:str,tenant_id:str,secret_value:str)->str:
    data = {'grant_type': "client_credentials",
            'resource': "https://graph.microsoft.com",
            'client_id': client_id,
            'client_secret': secret_value}

    URL = f"https://login.windows.net/{tenant_id}/oauth2/token?api-version=v1.0"
    # URL=f"https://login.microsoftonline.com/consumers?client_id={client_id}"
    r = requests.post(url=URL, data=data)
    j = json.loads(r.text)
    TOKEN = j["access_token"]
    return TOKEN


def get_all_users_profiles(token:str):
    HEADERS = {'Authorization': 'Bearer ' + token}
    response = requests.get(url="https://graph.microsoft.com/v1.0/users",headers=HEADERS)
    ret=response.json()
    return ret
def get_user_profile(token:str,user_id:str):
    HEADERS = {'Authorization': 'Bearer ' + token}
    response = requests.get(url=f"https://graph.microsoft.com/v1.0/users/{user_id}",headers=HEADERS)
    ret=response.json()
    return ret
def get_all_folders_of_user(token:str,user_id:str):
    HEADERS = {'Authorization': 'Bearer ' + token}
    response = requests.get(url=f"https://graph.microsoft.com/v1.0/users/{user_id}/drive/root",headers=HEADERS)
    ret=response.json()
    return ret