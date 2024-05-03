import cy_kit
from cyx.g_drive_services import GDriveService
import io
g=  cy_kit.singleton(GDriveService)
import json
import os
file_path =f"/home/vmadmin/python/cy-py/a-working/test.jpg"
token = g.get_access_token_from_refresh_token("lv-docs")
import requests
headers = {"Authorization": "Bearer "+token, "Content-Type": "application/json"}
import mimetypes
t, _ = mimetypes.guess_type(file_path)
params = {
    "name": "sample.jpg",
    "mimeType": t
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
    headers=headers,
    data=json.dumps(params)
)
location = r.headers['Location']
pos =0
data = bytes([0])
filesize = os.path.getsize(file_path)
upload_size =0
with open(file_path,"rb") as fs:
    while data:
        data = fs.read(1000)
        size  = len(data)
        upload_size+=size
        headers = {"Content-Range": f"bytes {pos}-{upload_size-1}/{upload_size}"}
        print(headers)
        pos+=size
        sd = io.BytesIO()
        sd.write(data)
        sd.seek(0)
        r = requests.patch(
            location,
            headers=headers,
            data=sd
        )
        print(r.text)
