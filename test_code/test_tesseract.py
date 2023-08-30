import gradio as gr
import pytesseract
from easyocr import Reader
import cy_kit
from cy_utils.langs.vn import  clear_accents
from cy_vn import get_config, predict_accents
get_config("/home/vmadmin/python/cy-py/share-storage/dataset/vn_predict")
def ocr(image):
    """Performs OCR on the given image."""
    text = pytesseract.image_to_string(image,lang="vie")
    return text
def ocr_easy(image):
    """Performs OCR on the given image."""
    reader = Reader(["vi"])
    text = reader.readtext(image,detail=0)
    txt = " ".join(text)
    txt2 = clear_accents(txt)
    txt_suggest = predict_accents(txt2)
    return txt+ "\n" + txt_suggest

app = gr.Interface(
    fn=ocr_easy,
    title="Tesseract OCR",
    description="Upload an image and I will perform OCR on it.",
    inputs=gr.Image(label="Image"),
    outputs=gr.outputs.HTML(label="Text"),
)

app.launch(
    server_port=8014,
    server_name="0.0.0.0"

)
