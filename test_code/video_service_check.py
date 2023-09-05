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
    info = video_svc.get_info(img.orig_name)
    return info,info.__dict__
    # r = img_svc.read_with_block(img)
    # img_svc.draw_result(r,img)
    # # global working_path
    # # tmp_dir= os.path.join(working_path,"tmp")
    # # os.makedirs(tmp_dir,exist_ok=True)
    # # new_file= f"{tmp_dir}/{uuid.uuid4().__str__()}.png"
    # # cylibs.save_numpy_array_as_image(img,new_file)
    # # lans,score = cylibs.detect_image_lang(new_file)
    # svc.read_with_block(img)
    # return cylibs.read_text_from_image(img,["vi","en","ch_sim"],
    #                                    f"/home/vmadmin/python/v6/file-service-02/share-storage/dataset/easyocr")
    # return img,{}
# with gr.Blocks() as demo:
input_gallary = gr.Image(label='Image Input', source="upload")
upload_video = gr.File(label='Image Input', source="upload")

io = gr.Interface(fn=run, inputs=[upload_video], outputs=['text','json'], title='Test EasyOCR',
description='This is the test of Easy OCR')
io.launch(
server_name="0.0.0.0",
    server_port=8014)