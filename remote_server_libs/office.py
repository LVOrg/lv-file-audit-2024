import sys
import pathlib
import traceback
import typing
import uuid
import hashlib
import urllib.request
sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os.path
from tqdm import tqdm
from fastapi import FastAPI, Body
import tempfile

temp_processing_file = os.path.join("/mnt/files","__lv-files-tmp__")
temp_path = os.path.join(temp_processing_file,"tmp-upload")
os.makedirs(temp_processing_file,exist_ok=True)
os.makedirs(temp_path,exist_ok=True)
tempfile.tempdir = temp_path
from remote_server_libs.utils import download_file
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
__memcache_server__ = "localhost:11211"
app = FastAPI()
from remote_server_libs.utils import libs
import cy_file_cryptor.context
try:
    cy_file_cryptor.context.set_server_cache(__memcache_server__)
except:
    print(traceback.format_exc())
import cy_file_cryptor.wrappers
import io
from fastapi import Request, HTTPException
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
        raise ex




@app.get("/")
async def root():
    return {"message": "Hello World!"}
@app.post("/settings")
async def do_settings(memcache_server:str):
    try:
        cy_file_cryptor.context.set_server_cache(memcache_server)
        return "OK"
    except:
        return traceback.format_exc()
@app.post("/image-from-office")
async def image_from_office(officeFile: UploadFile = File(...) ):
    content = await officeFile.read()
    file_name = f"{str(uuid.uuid4())}{pathlib.Path(officeFile.filename).suffix}"
    file_path = os.path.join(temp_path,file_name)
    with open(file_path,"wb") as fs:
        fs.write(content)
    command = ["/usr/bin/soffice",
               "--headless",
               "--convert-to",
               "png", "--outdir",
               f"{temp_path}",
               f"{file_path}"]
    txt_command = " ".join(command)
    libs.execute_command_with_polling(txt_command)
    os.remove(file_path)

    return {
        "filename": officeFile.filename,
        "content_type": officeFile.content_type,
        # Add information about processed image here (if applicable)
        # "width": resized_img.width,
        # "height": resized_img.height,
    }
@app.get("/hz")
async def hz():
    return "OK"
@app.post("/get-image")
async def image_from_office_from_share_file(
        local_file:typing.Optional[str]=Body(embed=True,default=None),
        remote_file:typing.Optional[str]=Body(embed=True,default=None),
        memcache_server:str=Body(embed=True)


):
    try:
        import cy_file_cryptor.context
        memcache_server = os.getenv("MEMCACHED_SERVER") or memcache_server
        cy_file_cryptor.context.set_server_cache(memcache_server)
        dir_of_file = temp_processing_file
        process_file = None
        if isinstance(local_file,str):
            if os.path.isfile(local_file):
                hash_object = hashlib.sha256(local_file.encode())
                load_file_name = hash_object.hexdigest()

                process_file = f"{load_file_name}{pathlib.Path(local_file).suffix}"
                with open(process_file,"wb") as fw:
                    with open(local_file,"rb") as fr:
                        data = fr.read(1024*1024)
                        while data:
                            fw.write(data)
                            del data
                            data = fr.read(1024 * 1024)


        if process_file is None:
            if remote_file.startswith("http://") or remote_file.startswith("https://"):
                hash_object = hashlib.sha256(remote_file.encode())
                load_file_name = hash_object.hexdigest()
                process_file = f"{load_file_name}{pathlib.Path(local_file).suffix}"
                process_file, error =download_file.download_file_with_progress(
                    url=remote_file, filename=process_file
                )
                if error:
                    return error
        if process_file is None:
            return dict(code="FileNotFound",message="File was not found")
        command = ["/usr/bin/soffice",
                   "--headless",
                   "--convert-to",
                   "png", "--outdir",
                   f"{dir_of_file}",
                   f"{process_file}"]
        txt_command = " ".join(command)
        libs.execute_command_with_polling(txt_command)
        process_file_name = pathlib.Path(process_file).stem

        ret_file = os.path.join(dir_of_file,process_file_name)+".png"
        if os.path.isfile(ret_file):
            os.remove(process_file)
            return dict(image_file=ret_file, content_file=process_file )
        else:
            return dict(error=dict(code="CanNotRender",message=f"{local_file} or {remote_file} can not render"))
    except:
        return dict(error=dict(code="ERR500", message=traceback.format_exc()))

if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port=int(x.split("=")[1])
    uvicorn.run("office:app", host="0.0.0.0", port=port)



