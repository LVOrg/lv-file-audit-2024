import datetime
import shutil
import sys
import pathlib
import traceback
import typing
import hashlib
# import fitz
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
from PyPDF2 import PdfReader, PdfWriter
import img2pdf

import fitz
import typing
import os


def do_clean_up(data):
    for split_page in list(data.keys()):
        if os.path.isfile(split_page):
            os.remove(split_page)
            print(f"delete file {split_page}")
        for x_page in data.get("pdf_from_images") or []:
            if os.path.isfile(x_page):
                os.remove(x_page)
                print(f"delete file {x_page}")
        for x_page in data.get("images") or []:
            if os.path.isfile(x_page):
                os.remove(x_page)
                print(f"delete file {x_page}")



def extract_files(pdf_path, output_dir) -> dict:
    """Extracts images from a PDF file and saves them to an output directory.

  Args:
    pdf_path: Path to the PDF file.
    output_dir: Directory to save extracted images.
  """
    os.makedirs(output_dir,exist_ok=True)
    ret = {}
    reader = PdfReader(open(pdf_path, 'rb'))
    num_pages = len(reader.pages)

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        output_filename = os.path.join(output_dir, f"{page_num}-split.pdf")
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(open(output_filename, 'wb'))
        ret[output_filename] = dict()
    for split_page in list(ret.keys()):
        doc = fitz.open(split_page)
        page = doc[0]
        ret[split_page]["images"] = []
        ret[split_page]["pdf_from_images"] = []
        img_id =0
        for img in page.get_images():
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            # Save image to output directory
            output_path = f"{split_page}_{img_id}_{xref}.{ext}"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
                ret[split_page]["images"] += [output_path]
            with open(f"{output_path}.pdf", "wb") as f:
              f.write(img2pdf.convert([output_path]))
            ret[split_page]["pdf_from_images"]+=[f"{output_path}.pdf"]
            img_id+=1
    return ret
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


def clear_cosnole():
    # print('\033[2J\033[H', end='')
    print("----------------------------------------------------")


def do_ocr_file(x_file:str):
    page_out_put=f"{x_file}-ocr.pdf"
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
                           x_file,
                           page_out_put]
            subprocess.run(command)
    except:
        print(traceback.format_exc())
    return page_out_put if os.path.isfile(page_out_put) else None


def concat_content(contents):
    txt_content=" ".join([x for x in contents if x is not None])
    for x in ['\n','\r','\t']:
        txt_content = txt_content.replace(x, " ")
    txt_content = txt_content.rstrip(" ").lstrip(" ")
    while "  " in txt_content:
        txt_content = txt_content.replace("  "," ")
    return txt_content


@app.post("/get-content")
async def content_from_pdf(
        tika_server: str = Body(embed=True),
        remote_file: str = Body(embed=True)

):
    clear_cosnole()
    print(remote_file)
    print(tika_server)
    start_time= datetime.datetime.utcnow()
    hash_object = hashlib.sha256(remote_file.encode())
    load_file_name = hash_object.hexdigest()
    process_file = os.path.join(temp_path,f"{load_file_name}-input.pdf")
    process_file, error = download_file.download_file_with_progress(
        url=remote_file, filename=process_file
    )
    output_dir = os.path.join(temp_processing_file,load_file_name)
    all_files = extract_files(process_file, output_dir) or {}
    contents = []
    for file in all_files.keys():
        parsed_data = parser.from_file(file, serverEndpoint=tika_server)
        contents += [parsed_data.get("content", "")]
        for x_file in all_files[file].get("pdf_from_images") or []:
            print(x_file)
            ocr_file= do_ocr_file(x_file)
            if ocr_file:
                parsed_data = parser.from_file(ocr_file, serverEndpoint=tika_server)
                contents += [parsed_data.get("content", "")]
    txt_content = concat_content(contents)
    do_clean_up(all_files)
    shutil.rmtree(output_dir,ignore_errors=True)
    return  dict(result=txt_content,time= (datetime.datetime.utcnow()-start_time).total_seconds())
if __name__ == "__main__":
    port = 8087
    for x in sys.argv:
        if x.startswith("port="):
            port = int(x.split("=")[1])
    uvicorn.run("ocr:app", host="0.0.0.0", port=port)
# docler run --entrypoint /app/mya
#import curses_util

# def handle_input(console, input):
#     console.log("Got input: " + input) #Logs result to the output window.
# from curses_util.console import SimpleConsole
# console = SimpleConsole(handle_input)
# console.log("Welcome")
#docker run -it --entrypoint /bin/bash -v /home/vmadmin/python/cy-py/remote_server_libs:/remote_server_libs -p 8087:8087 nttlong/ocr-my-pdf-api:9