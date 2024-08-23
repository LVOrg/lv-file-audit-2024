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
from  remote_server_libs.utils.pdf2image import get_image
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
from fastapi import Request, HTTPException, Response
from remote_server_libs.utils.pdf2image import get_image
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
def download_file(url,out_put_dir):

    """Downloads a file from the given URL to the specified output path.

    Args:
      url: The URL of the file to download.
      output_path: The local path where the file should be saved.
      :param url:
      :param output_path:
    """
    try:
        file_name = hashlib.sha256(url.encode('utf8')).hexdigest()
        file_ext = pathlib.Path(url.split("?")[0]).suffix
        output_path = os.path.join(out_put_dir,file_name+file_ext)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return output_path, None
    except Exception as ex:
        return None, dict(error=dict(code="CanNotDownloadFile", message= traceback.format_exc()))
@app.middleware("http")
async def log_request(request: Request, call_next):
    """Logs information about incoming requests."""
    try:
        path = request.url.path
        method = request.method
        headers = request.headers
        print(f"Path: {path}, Method: {method}, Headers: {headers}")
        response = await call_next(request)
        return response
    except Exception as ex:
        print(traceback.format_exc())
        return Response(content=traceback.format_exc(),status_code=500)

temp_dir = "/tmp/download"
@app.get("/hz")
async def hz():
    return "OK"


@app.post("/get-image")
async def image_from_pdf(
        download_url: typing.Optional[str] = Body(embed=True, default=None),
        upload_url: typing.Optional[str] = Body(embed=True, default=None)

):

    os.makedirs(temp_dir,exist_ok=True)
    ret_file,error = download_file(download_url,temp_dir)
    if error:
        return error
    image_file = get_image(ret_file,temp_dir)
    upload_file(upload_url, image_file)
    os.remove(ret_file)
    return ret_file


if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("pdf_api:app", host="0.0.0.0", port=port)
