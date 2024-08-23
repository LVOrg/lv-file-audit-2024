import sys
import pathlib
import traceback
import typing
import hashlib

sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os.path
from fastapi import FastAPI, Body
import tempfile

temp_processing_file = os.path.join("/mnt/files", "__lv-files-tmp__")
temp_path = os.path.join(temp_processing_file, "tmp-upload")
os.makedirs(temp_processing_file, exist_ok=True)
os.makedirs(temp_path, exist_ok=True)
tempfile.tempdir = temp_path
from remote_server_libs.utils import download_file
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()
import requests
from remote_server_libs.utils.video2image import get_image
def upload_file(url_upload_file, thumb_file_path):
  """Uploads a file to a given URL.

  Args:
    url_upload_file: The URL endpoint for file upload.
    thumb_file_path: The path to the file to be uploaded.

  Returns:
    The response from the server.
  """

  files = {'content': open(thumb_file_path, 'rb')}
  response = requests.post(url_upload_file, files=files)
  ret= response.json()
  return ret
@app.get("/hz")
async def hz():
    return "OK"


@app.post("/get-image")
async def image_from_pdf(
        download_url: typing.Optional[str] = Body(embed=True, default=None),
        upload_url: typing.Optional[str] = Body(embed=True, default=None)

):


    temp_path = "/tmp/download"
    os.makedirs(temp_path,exist_ok=True)
    image_of_video_file = get_image(download_url,temp_path)
    upload_file(upload_url,image_of_video_file)
    os.remove(image_of_video_file)
    if os.path.isfile(image_of_video_file):

        return dict(image_file=image_of_video_file, content_file=None)
    else:
        return dict(error=dict(code="CanNotRender", message=f"{download_url} can not render"))


if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("video:app", host="0.0.0.0", port=port)
