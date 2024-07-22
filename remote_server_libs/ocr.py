import datetime
import shutil
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
from PyPDF2 import PdfReader, PdfWriter
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
    split_folder = os.path.join(temp_path,f"{load_file_name}-spliter")
    os.makedirs(split_folder,exist_ok=True)
    reader = PdfReader(open(process_file, 'rb'))
    num_pages = len(reader.pages)
    print(f"Process {num_pages} page(s)")
    pages_list = []
    for page_num in range(num_pages):
        page = reader.pages[page_num]
        output_filename = os.path.join(split_folder,f"{page_num}.pdf")
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(open(output_filename, 'wb'))
        pages_list+=[output_filename]
    content = []
    print(pages_list)
    for page in pages_list:
        page_out_put = f"{page}-output"
        page_out_put_convert = f"{page_out_put}.pdf"
        cmd_convert = ["gs", "-o", page_out_put_convert, "-sDEVICE=pdfwrite", "-dFILTERTEXT", page]
        detect_page = page_out_put_convert if os.path.isfile(page_out_put_convert) else page
        try:
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
                           detect_page,
                           page_out_put]
            subprocess.run(command)
            parsed_data = parser.from_file(page_out_put, serverEndpoint=tika_server)
            content += [parsed_data.get("content", "")]
        except:
            parsed_data = parser.from_file(page, serverEndpoint=tika_server)
            content+=[parsed_data.get("content","")]


    txt_content = " ".join([x for x in content if x is not None])
    for x in ['\n','\r','\t']:
        txt_content = txt_content.replace(x, " ")
    txt_content = txt_content.rstrip(" ").lstrip(" ")
    while "  " in txt_content:
        txt_content = txt_content.replace("  "," ")
    if os.path.isfile(process_file_output):
        os.remove(process_file_output)
    if os.path.isfile(process_file):
        os.remove(process_file)
    if os.path.isfile(convert_process_file):
        os.remove(convert_process_file)
    if os.path.isdir(split_folder):
        shutil.rmtree(split_folder,ignore_errors=True)
    return dict(result=txt_content,time= (datetime.datetime.utcnow()-start_time).total_seconds())



if __name__ == "__main__":
    port = 8087
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("ocr:app", host="0.0.0.0", port=port)
# docler run --entrypoint /app/mya