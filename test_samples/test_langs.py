import typing
import pytesseract
from PIL import Image
import PIL
from langdetect import detect_langs
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
# '<full_path_to_your_tesseract_executable>'
# # Include the above line, if you don't have tesseract executable in your path
#
# # Example tesseract_cmd: 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
from cyx.linguistics import vn_remove_accents
from cy_vn.accent_predictor import get_config,predict_accents
get_config("/home/vmadmin/python/cy-py/share-storage/cy_vn")
def get_langs(image):
    img  = image
    if isinstance(image,str):
        img = Image.open('test.png')
    sample_text = pytesseract.image_to_string(img,lang="vie")
    print(sample_text)
    sample_text= vn_remove_accents(sample_text)
    print(sample_text)
    sample_text = predict_accents(sample_text)

    return detect_langs(sample_text)

