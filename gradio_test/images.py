import os.path
import sys
import pathlib
import gradio as gr
sys.path.append("/web")
if os.path.isdir("/app/cyx"):
    sys.path.append("/app")
    working_dir = "/app"
else:
    working_dir = pathlib.Path(__file__).parent.parent.__str__()

dataset_path = os.path.abspath(
    os.path.join(working_dir,"share-storage/dataset/easyocr")
)
print(f"dataset_payh='{dataset_path}'")
from cyx.utils import easyocr_get_langs_suport
from cyx.document_layout_analysis.system import get_tesseract_languages
# reader=None
import easyocr
langs= easyocr_get_langs_suport()
if easyocr.__version__!="1.6.2":
    raise Exception(f"Expected easyocr 1.6.2, but found {easyocr.__version__}")
print(easyocr_get_langs_suport())
def hello(inp,lan):

    # global reader
    # global langs
    # if reader is None:
    try:
        reader = easyocr.Reader(
            [lan], gpu=False,
            model_storage_directory=dataset_path
        )
    except Exception as e:
        return None,e
    ret =reader.readtext(inp)
    return ret,None
with gr.Blocks() as demo:
    lange_select=gr.Dropdown(
            langs, value=langs, multiselect=False, label="Language", info=""
        )

    input_gallary = gr.Image(label='Image Input', source="upload")
io = gr.Interface(fn=hello, inputs=[input_gallary,lange_select], outputs=['text','text'], title='Test EasyOCR',
    description='This is the test of Easy OCR')
io.launch(
server_name="0.0.0.0",
    server_port=8012


)