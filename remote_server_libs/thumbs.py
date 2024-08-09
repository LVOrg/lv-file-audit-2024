import sys
import pathlib
import threading
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

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()


import requests
import hashlib
@app.get("/hz")
async def hz():
    return "OK"


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
from PIL import Image
import webp
def do_scale_size( file_path, size):
    """
    Create scale size of image in file_path in size of square size ex: size=120 square is 120x120
    The scale file name is in format {size}.webp an place at the same folder of file_path
    :param file_path:
    :param size:
    :return:
    """

    Image.MAX_IMAGE_PIXELS = None
    ret_image_path = os.path.join(pathlib.Path(file_path).parent.__str__(), f"{size}.webp")
    temp_ret_image_path = os.path.join(pathlib.Path(file_path).parent.__str__(), f"{size}_tmp.webp")
    with Image.open(file_path) as img:
        original_width, original_height = img.size
        if size > max(original_width, original_height):
            size = int(max(original_width, original_height))
        rate = size / original_width
        w, h = size, int(original_height * rate)
        if original_height > original_width:
            rate = size / original_height
            w, h = int(original_width * rate), size
        scaled_img = img.resize((w, h))  # High-quality resampling


        webp.save_image(scaled_img, ret_image_path,
                        lossless=True)  # Set lossless=False for lossy compression
        scaled_img.close()
        del scaled_img

        return ret_image_path
"""
            size=size,
            url_of_thumb_service = url_of_thumb_service,
            url_of_image = url_of_image,
            url_upload_file = url_upload_file
"""
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
@app.post("/get-thumb")
async def generate_thumbs(
        size:int=Body(embed=True),
        url_of_image: str= Body(embed=True),
        url_upload_file: str= Body(embed=True)

):

    def runner():
        dir_of_file = temp_processing_file
        process_file = None

        image_file,error = download_file(url_of_image,temp_processing_file)
        if error:
            return  error
        thumb_file_path = do_scale_size(image_file,size)
        upload_file(url_upload_file, thumb_file_path)
        return "OK"
    threading.Thread(target=runner).start()
    return "Processing"










if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("thumbs:app", host="0.0.0.0", port=port)
