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
from remote_server_libs.utils import libs
import cy_file_cryptor.context

import cy_file_cryptor.wrappers
import io
from remote_server_libs.utils.video2image import get_image

@app.get("/hz")
async def hz():
    return "OK"


@app.post("/get-image")
async def image_from_pdf(
        local_file: typing.Optional[str] = Body(embed=True, default=None),
        remote_file: typing.Optional[str] = Body(embed=True, default=None),
        memcache_server: str = Body(embed=True)

):
    import cy_file_cryptor.context
    cy_file_cryptor.context.set_server_cache(memcache_server)
    dir_of_file = temp_processing_file
    process_file = None

    image_of_video_file = get_image(remote_file,temp_processing_file)



    if os.path.isfile(image_of_video_file):

        return dict(image_file=image_of_video_file, content_file=None)
    else:
        return dict(error=dict(code="CanNotRender", message=f"{local_file} or {remote_file} can not render"))


if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("video:app", host="0.0.0.0", port=port)
