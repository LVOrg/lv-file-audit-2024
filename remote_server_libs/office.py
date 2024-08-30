import sys
import pathlib
import threading
import traceback
import typing
import uuid
import hashlib
import urllib.request

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
# from remote_server_libs.utils import download_file
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()
from remote_server_libs.utils import libs
import requests


def download_content(url_of_content: str, output_dir: str):
    """Downloads content from the given URL and saves it to a file.

      Args:
        url_of_content: The URL of the content to download.
      """
    filename = hashlib.sha256(url_of_content.encode()).hexdigest()
    os.makedirs(output_dir, exist_ok=True)
    full_file_name = os.path.join(output_dir, filename)
    try:
        response = requests.get(url_of_content, stream=True)
        response.raise_for_status()  # Raise an exception for error HTTP statuses
        # Determine the filename based on the content-disposition header
        with open(full_file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)

        print(f"Content downloaded successfully: {full_file_name}")
        return full_file_name

    except requests.exceptions.RequestException as e:
        print(traceback.format_exc())


import io
from fastapi import Request, HTTPException


# @app.middleware("http")
# async def log_request(request: Request, call_next):
#     """Logs information about incoming requests."""
#     try:
#         path = request.url.path
#         method = request.method
#         headers = request.headers
#         print(f"Path: {path}, Method: {method}, Headers: {headers}")
#         response = await call_next(request)
#         return response
#     except Exception as ex:
#         print(traceback.format_exc())



def run_libre_office_convert_to_image(file_path: str) -> str | None:
    """

    :param file_path:
    :return:
    """
    output_dir = pathlib.Path(file_path).parent.__str__()
    command = ["/usr/bin/soffice",
               "--headless",
               "--convert-to",
               "png", "--outdir",
               f"{output_dir}",
               f"{file_path}"]
    txt_command = " ".join(command)
    print(txt_command)
    libs.execute_command_with_polling(txt_command)
    return f"{file_path}.png"
def upload_file(url_upload_file, image_file_path):
  """Uploads a file to a given URL.

  Args:
    url_upload_file: The URL endpoint for file upload.
    image_file_path: The path to the file to be uploaded.

  Returns:
    The response from the server.
  """
  assert isinstance(url_upload_file,str),"url_upload_file is invalid"

  files = {'content': open(image_file_path, 'rb')}
  response = requests.post(url_upload_file, files=files)
  ret = response.json()
  return ret

@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.post("/get-image")
async def get_image_from_office(
        url_of_content: str = Body(embed=True),
        url_upload_file: str = Body(embed=True),
        run_in_thread:bool = Body(embed=True,default=True)
):
    def runner():
        print(run_in_thread)
        file_download = download_content(url_of_content, temp_processing_file)
        print(url_of_content)

        image_file_path = run_libre_office_convert_to_image(
            file_path=file_download
        )
        upload_file(
            url_upload_file=url_upload_file,
            image_file_path=image_file_path
        )
    if run_in_thread:
        threading.Thread(target=runner).start()
        return dict(
            url_of_content=url_of_content,
            url_upload_file=url_upload_file,
            # file_download=file_download
        )
    else:
        try:
            runner()
            return dict(
                url_of_content=url_of_content,
                url_upload_file=url_upload_file,
                # file_download=file_download
            )
        except Exception as ex:
            return dict(
                error=dict(
                    code=repr(ex),
                    message = traceback.format_exc()
                )
            )





@app.get("/hz")
async def hz():
    return "OK"


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("office:app", host="0.0.0.0", port=port)
