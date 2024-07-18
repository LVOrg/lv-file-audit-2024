import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from fastapi import FastAPI, UploadFile
from typing import Optional

app = FastAPI()

@app.post("/ocrm-pdf/")
async def ocr_pdf(file_path:str,url_file:str):
    return "OK"
