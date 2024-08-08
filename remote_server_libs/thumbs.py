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

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

import cy_file_cryptor.context

import cy_file_cryptor.wrappers
import io
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


@app.post("/generate-thumbs")
async def image_from_pdf(
        local_file: typing.Optional[str] = Body(embed=True, default=None),
        remote_file: typing.Optional[str] = Body(embed=True, default=None),
        memcache_server: str = Body(embed=True)

):
    import cy_file_cryptor.context
    memcache_server = os.getenv("MEMCACHED_SERVER") or memcache_server
    cy_file_cryptor.context.set_server_cache(memcache_server)
    dir_of_file = temp_processing_file
    process_file = None

    image_of_video_file,error = download_file(remote_file,temp_processing_file)
    if error:
        return  error



    if os.path.isfile(image_of_video_file):

        return dict(image_file=image_of_video_file, content_file=None)
    else:
        return dict(error=dict(code="CanNotRender", message=f"{local_file} or {remote_file} can not render"))


if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("thumbs:app", host="0.0.0.0", port=port)
