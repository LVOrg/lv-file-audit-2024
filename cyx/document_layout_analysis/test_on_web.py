import sys
import pathlib

working_path = pathlib.Path(__file__).parent.parent.parent.__str__()
print(f"app path = {working_path}")
import os

sys.path.append(working_path)
import cyx.document_layout_analysis.system
# cyx.document_layout_analysis.system.set_languages("Vietnamese")
cyx.document_layout_analysis.system.set_offline_dataset(True)
from cyx.common.share_storage import ShareStorageService
import cy_kit
share_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.abspath(
        os.path.join(share_storage_service.get_root(),"dataset")
    )
)
import cy_kit
import gradio as gr
from  cyx.document_layout_analysis.table_ocr_service import TableOCRService

table_ocr_service = cy_kit.singleton(TableOCRService)
import transformers.file_utils
transformers.file_utils.is_pytesseract_available()

os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"

demo = gr.Blocks(css="scrollbar.css")

with demo:
    with gr.Box():
        gr.Markdown("<h1><center>deepdoctection - A Document AI Package</center></h1>")
        gr.Markdown("<strong>deep</strong>doctection is a Python library that orchestrates document extraction"
                    " and document layout analysis tasks using deep learning models. It does not implement models"
                    " but enables you to build pipelines using highly acknowledged libraries for object detection,"
                    " OCR and selected NLP tasks and provides an integrated frameworks for fine-tuning, evaluating"
                    " and running models.\n This pipeline consists of a stack of models powered by <strong>Detectron2"
                    "</strong> for layout analysis and table recognition and <strong>DocTr</strong> for OCR.")
    with gr.Box():
        gr.Markdown("<h2><center>Upload a document and choose setting</center></h2>")
        with gr.Row():
            with gr.Column():
                with gr.Tab("Image upload"):
                    with gr.Column():
                        inputs = gr.Image(type='numpy', label="Original Image")
                with gr.Tab("PDF upload (only first image will be processed) *"):
                    with gr.Column():
                        inputs_pdf = gr.File(label="PDF")
                    gr.Markdown("<sup>* If an image is cached in tab, remove it first</sup>")
            # with gr.Column():
            #     gr.Examples(
            #         examples=[path.join(app_path, "sample_1.jpg"), path.join(app_path, "sample_2.png")],
            #         inputs = inputs)
            #     gr.Examples(examples=[path.join(app_path, "sample_3.pdf")], inputs = inputs_pdf)

        with gr.Row():
            tok_input = gr.CheckboxGroup(
                table_ocr_service._DETECTIONS,
                value=table_ocr_service._DETECTIONS,
                label="Additional extractions", interactive=True
            )
        with gr.Row():
            btn = gr.Button("Run model", variant="primary")

    with gr.Box():
        gr.Markdown("<h2><center>Outputs</center></h2>")
        with gr.Row():
            with gr.Column():
                with gr.Box():
                    gr.Markdown("<center><strong>Contiguous text</strong></center>")
                    image_text = gr.Textbox()
                with gr.Box():
                    gr.Markdown("<center><strong>Table</strong></center>")
                    html = gr.HTML()
                with gr.Box():
                    gr.Markdown("<center><strong>JSON</strong></center>")
                    json = gr.JSON()
            with gr.Column():
                with gr.Box():
                    gr.Markdown("<center><strong>Layout detection</strong></center>")
                    image_output = gr.Image(type="numpy", label="Output Image")

    btn.click(fn=table_ocr_service.analyze_image_or_pdf, inputs=[inputs, inputs_pdf, tok_input],
              outputs=[image_output, image_text, html, json])
from cyx.common import config
demo.launch(

    share=True,
    server_port=8013,
    server_name="0.0.0.0"
)
