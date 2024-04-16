import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())

import uuid

import gradio as gr
import os
import requests
import subprocess
import  libs

def download_file(url, download_to_file):
    """
    Downloads a file from the given URL to the specified location.

    Args:
        url (str): The URL of the file to download.
        download_location (str): The path to the directory where the file should be saved.

    Returns:
        None

    Raises:
        Exception: If any error occurs during the download process.
    """

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes



        with open(download_to_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return download_to_file

    except Exception as e:
        print(f"An error occurred during download: {e}")
os.makedirs("/socat-share",exist_ok=True)
def process_text(text,is_return_base_64_image):
    try:
        # Replace this with your desired text processing logic
        processed_text = text.upper() + " (processed)"
        file_id = str(uuid.uuid4())
        file_download = os.path.join("/socat-share",file_id)
        download_file(text,file_download)
        #/usr/bin/soffice --headless --convert-to png --outdir /socat-share /cmd/office_image.py
        command = ["/usr/bin/soffice",
                   "--headless",
                   "--convert-to",
                   "png", "--outdir",
                   f"/socat-share",
                   f"{file_download}"]
        txt_command= " ".join(command)
        libs.execute_command_with_polling(txt_command)
        os.remove(file_download)

    except Exception as ex:
        raise ex
    if is_return_base_64_image:
        return f"/socat-share/{file_id}.png",f"/socat-share/{file_id}.png"
    else:
        return None, f"/socat-share/{file_id}.png"


iface = gr.Interface(
    fn=process_text,
    inputs=["textbox",gr.Checkbox(label="Return base64 image", value=True)],
    outputs=["image","textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)

iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1113
)
