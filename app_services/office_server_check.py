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
import webp
print("OK")