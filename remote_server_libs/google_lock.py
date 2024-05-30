import sys
import pathlib
import threading
import traceback
import typing
import hashlib
import google.auth.exceptions
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
import io
from fastapi import Request, HTTPException, Response
from remote_server_libs.utils import g_api
distribute_lock_server= os.getenv("LOCK_SERVER") or "172.16.7.99:30962"
from kazoo.client import KazooClient
zk = KazooClient(distribute_lock_server)
zk.start()
lock_dict=dict()
@app.middleware("http")
async def log_request(request: Request, call_next):
    """Logs information about incoming requests."""
    try:

        response = await call_next(request)
        return response
    except Exception as ex:
        print(traceback.format_exc())
        return Response(content=traceback.format_exc(),status_code=500)
lock = threading.Lock()
def get_locker(client_id:str):
    if lock_dict.get(client_id):
        return lock_dict[client_id]
    if lock.acquire(timeout=1):
        try:
            lock_dict[client_id] = zk.Lock(client_id)
            return lock_dict[client_id]
        finally:
            lock.release()

@app.get("/hz")
async def hz():
    return "OK"


@app.post("/get-directory")
async def get_directory(
        refresh_token:str=Body(embed=True),
        client_id:str=Body(embed=True),
        client_secret:str=Body(embed=True),
        g_service_name:str=Body(embed=True,default="v3/drive"),
        g_directory_path:str=Body(embed=True),
        g_filename:str=Body(embed=True)

):
    locker = get_locker(client_id)
    if locker.acquire(timeout=30):
        try:
            service = g_api.get_service(refresh_token,client_id,client_secret)
            IsExit, Folder_id ,error =g_api.do_validate(service,g_directory_path,g_filename)
            if error:
                return dict(
                    error=error
                )
            return dict(
                result=dict(
                    is_exist=IsExit,
                    folder_id=Folder_id
                )
            )
        except google.auth.exceptions.RefreshError as ex:
            return dict(
                    error=dict(
                        Code=ex.args[1].get('error'),
                        Message=ex.args[1].get('error_description')
                    )
                )
        finally:
            locker.release()





if __name__ == "__main__":
    port = os.getenv("PORT") or 8001

    uvicorn.run("google_lock:app", host="0.0.0.0", port=port)
