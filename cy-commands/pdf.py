import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())

import uuid

import gradio as gr
import os
import requests
import subprocess
import  libs
import fitz
import pathlib
import os
import glob
import argparse
import json
def get_image(file_path: str,to_dir:str):
    pdf_file = file_path
    filename_only = pathlib.Path(pdf_file).stem
    to_file = os.path.join(to_dir,f"{filename_only}.png")
    unique_dir = pathlib.Path(file_path).parent.__str__()

    image_file_path = os.path.join(unique_dir, f"{filename_only}.png")
    if os.path.isfile(image_file_path):
        return image_file_path
    if os.path.isfile(image_file_path):
        return image_file_path
    # To get better resolution
    zoom_x = 2.0  # horizontal zoom
    zoom_y = 2.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
    all_files = glob.glob(pdf_file)
    for filename in all_files:
        doc = fitz.open(filename)  # open document
        for page in doc:  # iterate through the pages
            pix = page.get_pixmap()  # render page to an image
            pix.save(to_file)  # store image as a PNG
            break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
        break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
    return to_file

os.makedirs("/socat-share",exist_ok=True)
def process_text(text,is_return_base_64_image):
    ret_file = None
    try:
        # Replace this with your desired text processing logic
        processed_text = text.upper() + " (processed)"
        file_id = str(uuid.uuid4())
        file_download = os.path.join("/socat-share",file_id)
        libs.download_file(text,file_download)

        ret_file = get_image(file_download,"/socat-share")
        os.remove(file_download)

    except Exception as ex:
        raise ex
    if is_return_base_64_image:
        return ret_file,ret_file
    else:
        return None, ret_file


iface = gr.Interface(
    fn=process_text,
    inputs=["textbox",gr.Checkbox(label="Return base64 image", value=True)],
    outputs=["image","textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)

iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1112
)
