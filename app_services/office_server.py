import os.path
import pathlib
import shutil
import subprocess
working_dir = pathlib.Path(__file__).parent.parent.__str__()
package_working_dir = pathlib.Path(__file__).parent.__str__()
tmp_dir = os.path.join(package_working_dir,"tmp")
os.makedirs(tmp_dir,exist_ok=True)
import uuid
os.environ["GRADIO_TEMP_DIR"] = tmp_dir
import gradio as gr
import cy_kit
import webp
libre_office_path = f"/bin/soffice"
uno = f"Negotiate=0,ForceSynchronous=1;"
user_profile_dir = "/tmp/tmp-libre-office-user-profile"
if not os.path.isfile(libre_office_path):
    raise Exception(f"{libre_office_path} was not found")
from PIL import Image

def scale_image(image_path, new_width:int, new_height:int)->str:
    """Scales an image while maintaining its aspect ratio.

    Args:
        image_path (str): Path to the image file.
        new_width (int, optional): Desired width of the scaled image.
        new_height (int, optional): Desired height of the scaled image.

    Returns:
        Image: The scaled image.
    """
    ret_image_path = os.path.join(pathlib.Path(image_path).parent.__str__(),f"{new_width}.webp")
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        rate = new_width/original_width
        w,h = new_width,int(original_height*rate)
        if original_height>original_width:
            rate = new_height / original_height
            w, h =  int(original_width * rate),new_height
        scaled_img = img.resize((w, h))  # High-quality resampling
        webp.save_image(scaled_img, ret_image_path, lossless=True)  # Set lossless=False for lossy compression

        return ret_image_path
def convert_office_file_to_image(file_path: str):
    tmp_dir = pathlib.Path(file_path).parent.__str__()
    full_user_profile_path = os.path.join(tmp_dir, "user-profiles")
    output_unique_dir = os.path.join(tmp_dir, "result")
    output_file_name = pathlib.Path(file_path).stem + ".png"
    pid = subprocess.Popen(
        [
            libre_office_path,
            '--headless',
            '--convert-to', 'png',
            f"--accept={uno}",
            f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
            '--outdir',
            output_unique_dir, file_path
        ],
        shell=False,
        start_new_session=True
        # creationflags=16
    )
    ret = pid.wait()
    ret_path = os.path.join(output_unique_dir, output_file_name)
    if not os.path.isfile(ret_path):
        shutil.rmtree(full_user_profile_path)
        raise Exception(f"Can not process file {file_path}")

    return ret_path


async def generate_image_from_office(file_path: str,scale:str,request:gr.Request):
    scales = [int(x) for x in scale.split(",") if x.isnumeric()]
    ret = convert_office_file_to_image(file_path)
    ret_list = []
    for x in scales:
        img = scale_image(ret,x,x)
        ret_list+=[request.headers['origin']+"/file="+ img]
    os.remove(file_path)
    return ret_list



gr = gr.Interface(fn=generate_image_from_office,
                    inputs=[
                        "file",
                        gr.Textbox(placeholder="Enter scale value here", value="60,120,240,480,600,700")],
                    outputs=[
                        "textbox"
                    ])
gr.launch(

    share=True,
    server_port=8014,
    server_name="0.0.0.0"
)
