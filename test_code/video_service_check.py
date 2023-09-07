import os.path
import pathlib
import sys
import uuid



working_path = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_path)
import cy_services.ocr.easy
import cy_kit
# file_path=f"/home/vmadmin/python/v6/file-service-02/share-storage/tmp-file-processing/sync/lv-docs/0ea12921-1118-42a1-bd64-943df04e27e0.png"
# img=cylibs.load_image_as_numpy_array(file_path)
# print(img)
import gradio as gr
# import cy_services
# svc= cylibs.singleton(cy_services.ocr.easy.ReadTextService).ins
import cylibs
from gradio import components
from cyx.video.video_services import VideoService
def run(img):
    # img_svc = cy_kit.singleton(cy_services.ocr.easy.ReadTextService)
    video_svc = cy_kit.singleton(VideoService)
    info = video_svc.get_info(img)
    ret_text = video_svc.extract_text(img)
    return info,ret_text
input_gallary = gr.Image(label='Image Input', source="upload")
upload_video = gr.Video(label='Video Input', source="upload")

io = gr.Interface(fn=run, inputs=[upload_video], outputs=['text','json'], title='Test EasyOCR',
description='This is the test of Easy OCR')
io.launch(
server_name="0.0.0.0",
    server_port=8014)