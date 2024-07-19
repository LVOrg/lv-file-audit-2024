import datetime
import sys
import pathlib
import traceback
import typing
import hashlib

sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.__str__())
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
from tika import parser

from fastapi import Request, HTTPException, Response
import subprocess
import ocrmypdf
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


@app.post("/get-content")
async def content_from_pdf(
        tika_server: str = Body(embed=True),
        remote_file: str = Body(embed=True)

):
    print(remote_file)
    print(tika_server)
    start_time= datetime.datetime.utcnow()
    hash_object = hashlib.sha256(remote_file.encode())
    load_file_name = hash_object.hexdigest()
    process_file = os.path.join(temp_path,f"{load_file_name}-input.pdf")
    convert_process_file = os.path.join(temp_path, f"{load_file_name}-convert.pdf")
    process_file_output = os.path.join(temp_path, f"{load_file_name}-output.pdf")
    process_file, error = download_file.download_file_with_progress(
        url=remote_file, filename=process_file
    )
    if error:
        return dict(error=dict(code="ERR500", message=traceback.format_exc()))
    else:
        cmd_convert =["gs", "-o", convert_process_file, "-sDEVICE=pdfwrite", "-dFILTERTEXT", process_file]
        print(" ".join(cmd_convert))
        subprocess.run(cmd_convert)
        print(convert_process_file)
        command = ["ocrmypdf",
                   "-l", "vie",
                   "--rotate-pages",
                   "--deskew",
                   # "--skip-text",
                   # "--redo-ocr",
                   # "--force-ocr",
                   # "--title", "My PDF",
                   "--jobs", "2",
                   "--output-type", "pdfa",
                   # "--tesseract - timeout", "300",
                   convert_process_file,
                   process_file_output]
        subprocess.run(command)
        parsed_data = {}
        parsed_data_original={}
        try:
            parsed_data = parser.from_file(process_file_output, serverEndpoint=tika_server)
        except:
            print(f"parse {process_file_output} with {tika_server} fail")
        try:
            parsed_data_original = parser.from_file(process_file, serverEndpoint=tika_server)
        except:
            print(f"parse {process_file} with {tika_server} fail")

        content = parsed_data.get("content","") +" "+ parsed_data_original.get("content","")
        for x in ['\n','\r','\t']:
            content = content.replace(x, " ")
        content = content.rstrip(" ").lstrip(" ")
        while "  " in content:
            content = content.replace("  "," ")
        if os.path.isfile(process_file_output):
            os.remove(process_file_output)
        if os.path.isfile(process_file):
            os.remove(process_file)
        if os.path.isfile(convert_process_file):
            os.remove(convert_process_file)
        return dict(result=content,time= (datetime.datetime.utcnow()-start_time).total_seconds())



if __name__ == "__main__":
    port = 8087
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("ocr:app", host="0.0.0.0", port=port)
