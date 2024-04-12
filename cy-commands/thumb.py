
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())

# import cy_file_cryptor.wrappers
import uuid

import gradio as gr
print(gr.__version__)
import os
import requests
import subprocess
import  libs
import webp
from PIL import Image

import json

is_install_encrypt = False
def get_thumb_path_from_image(in_path, size, main_file_path):
    global is_install_encrypt
    """Scales an image while maintaining its aspect ratio.

            Args:
                image_path (str): Path to the image file.
                new_width (int, optional): Desired width of the scaled image.
                new_height (int, optional): Desired height of the scaled image.

            Returns:
                Image: The scaled image.
            """
    if not is_install_encrypt:
        import cy_file_cryptor.wrappers
        is_install_encrypt = True
    ret_image_path = os.path.join(pathlib.Path(main_file_path).parent.__str__(), f"{size}.webp")
    temp_ret_image_path = os.path.join(pathlib.Path(main_file_path).parent.__str__(), f"{size}_tmp.webp")
    with Image.open(main_file_path) as img:
        original_width, original_height = img.size
        if size > max(original_width, original_height):
            size = int(max(original_width, original_height))
        rate = size / original_width
        w, h = size, int(original_height * rate)
        if original_height > original_width:
            rate = size / original_height
            w, h = int(original_width * rate), size
        scaled_img = img.resize((w, h))  # High-quality resampling

        from cy_file_cryptor.context import create_encrypt
        with create_encrypt(ret_image_path):
            webp.save_image(scaled_img, ret_image_path,
                            lossless=True)  # Set lossless=False for lossy compression

        return ret_image_path
def process_text(text,is_return_base_64_image):
    from cy_file_cryptor.context import set_server_cache

    data = json.loads(text)
    set_server_cache(data['mem_cache_server'])
    del data['mem_cache_server']
    ret = get_thumb_path_from_image(**data)
    return None,True



iface = gr.Interface(
    fn=process_text,
    inputs=["textbox",gr.Checkbox(label="Return base64 image", value=True)],
    outputs=["image","textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)

iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1114
)
