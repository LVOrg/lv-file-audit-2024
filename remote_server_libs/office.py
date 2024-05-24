import sys
import pathlib
import traceback
import uuid
import hashlib
import urllib.request
sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os.path
from tqdm import tqdm
from fastapi import FastAPI, Body
import tempfile
temp_path = os.path.join(pathlib.Path(__file__).parent.__str__(),"tmp-upload")
temp_processing_file = os.path.join("/mnt/files","__lv-files-tmp__")
os.makedirs(temp_processing_file,exist_ok=True)
os.makedirs(temp_path,exist_ok=True)
tempfile.tempdir = temp_path
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
@app.post("/image-from-office-from-share-file")
async def image_from_office_from_share_file(
        location:str=Body(embed=True)

):
    hash_object = hashlib.sha256(location.encode())
    load_file_name = hash_object.hexdigest()
    dir_of_file = temp_processing_file
    file_name = f"{load_file_name}{pathlib.Path(location).suffix}"
    if location.startswith("http://") or location.startswith("https://"):
        with urllib.request.urlopen(location) as response:
            if response.status>=200 and response.status<300:
                  with open(file_name, 'wb') as f:
                      f.write(response.read())
            else:
                return dict(error=dict(code="FileNotFound", message=f"{location} was not found"))
    elif not os.path.isfile(location):
        return dict(error=dict(code="FileNotFound",message=f"{location} was not found"))


    os.makedirs(dir_of_file,exist_ok=True)
    true_file = os.path.join(dir_of_file,file_name)
    with open(true_file,"wb") as fs_to:
        with open(location,"rb") as fs:
            data = fs.read(1020**2)
            while data:
                fs_to.write(data)
                del data
                data = fs.read(1020 ** 2)

    command = ["/usr/bin/soffice",
               "--headless",
               "--convert-to",
               "png", "--outdir",
               f"{dir_of_file}",
               f"{true_file}"]
    txt_command = " ".join(command)
    libs.execute_command_with_polling(txt_command)
    ret_file = os.path.join(dir_of_file,load_file_name)+".png"
    if os.path.isfile(ret_file):
        return dict(image_filr=ret_file, content_file=true_file )
    else:
        return dict(error=dict(code="CanNotRender",message=f"{location} can not render"))

if __name__ == "__main__":
    port = 8001
    for x in sys.argv:
        if x.startswith("port="):
            port=int(x.split("=")[1])
    uvicorn.run("office:app", host="0.0.0.0", port=port)



