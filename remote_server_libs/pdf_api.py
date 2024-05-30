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
from remote_server_libs.utils import libs
import cy_file_cryptor.context

import cy_file_cryptor.wrappers
import io
from fastapi import Request, HTTPException, Response
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
    memcache_server= os.getenv("MEMCACHED_SERVER") or memcache_server
    cy_file_cryptor.context.set_server_cache(memcache_server)
    dir_of_file = temp_processing_file
    process_file = None


    if process_file is None:
        """
        Download file from server
        """
        if remote_file.startswith("http://") or remote_file.startswith("https://"):
            hash_object = hashlib.sha256(remote_file.encode())
            load_file_name = hash_object.hexdigest()
            process_file = f"{load_file_name}{pathlib.Path(local_file).suffix}"
            process_file, error = download_file.download_file_with_progress(
                url=remote_file, filename=process_file
            )
            if error:
                return error
    if process_file is None:
        return dict(code="FileNotFound", message="File was not found")
    """
    Make an image from pdf file
    """
    image_of_pdf_file = get_image(process_file,temp_processing_file)
    process_file_name = pathlib.Path(process_file).stem

    ret_file = os.path.join(dir_of_file, process_file_name) + ".png"
    if os.path.isfile(ret_file):
        os.remove(process_file)
        return dict(image_file=ret_file, content_file=process_file)
    else:
        return dict(error=dict(code="CanNotRender", message=f"{local_file} or {remote_file} can not render"))


if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("pdf_api:app", host="0.0.0.0", port=port)
