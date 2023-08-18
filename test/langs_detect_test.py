

import gradio as gr
import pytesseract
from easyocr import Reader
import cy_kit
from cy_utils.langs.vn import clear_accents
from cy_vn import get_config, predict_accents
from test_samples.test_langs import get_langs
# import keras_ocr.tools
# import keras_ocr
import sys
# keras_ocr.tools.get_default_cache_dir()
import pytesseract
import re
from cyx.files_converter import convert_image_to_pdf, convert_file_ext
import ocrmypdf
import PyPDF2
from cyx.files_reader import read_text_from_pdf
from cyx.ext_libs.cy_utils import Files, Converter, Loggers, ContentReader,OCR, Tesseract,EasyOCR,Linguistics, Images
logger_dir = Loggers.get_directory()
def detect_image_lang(img_path):
    pdf_file = Files.convert_file_ext(img_path, "pdf")
    Converter.image_to_pdf(img_path, pdf_file)
    pdf_file_output = OCR.from_pdf(pdf_file)
    txt = ContentReader.read_text_from_pdf(pdf_file_output)
    return txt

def detect_image_lang_2(img_path):
    ret = Tesseract.get_boxes(img_path)
    return ret
def detect_image_lang_3(img_path):
    ret = Tesseract.get_text(img_path)
    langs = Linguistics.detect_langs(ret)
    seg_words= Linguistics.segment_word(ret)
    return dict(text=ret,seg_words=seg_words,langs=langs,langs_support = Tesseract.get_langs_support())
def detect_image_lang_4(img_path):
    ret,data, np_polylines = EasyOCR.get_data(img_path,langs=["vi","en"])
    poly_lines = [x["points"] for x in ret]
    img = Images.poly_lines(img_path,np_polylines)
    ret_txt= [  x["text"]  for x in ret     ]


    return img,ret_txt
def text_get_lang(image):
    """Performs OCR on the given image."""
    a = detect_image_lang(image)
    return a


app = gr.Interface(
    fn=detect_image_lang_4,
    title="Tesseract OCR",
    description="Upload an image and I will perform OCR on it.",
    inputs=gr.Image(label="Image", type="filepath"),
    outputs=[gr.Image(type="numpy"), "json"],
)

app.launch(
    server_port=8014,
    server_name="0.0.0.0"

)
