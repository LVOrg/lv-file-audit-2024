import pytesseract
from PIL import Image
from cy_utils import new_temp_file, graphics
import cv2
import numpy


def get_text_from_img(img: numpy.ndarray):
    text = pytesseract.image_to_string(img, lang="vie+eng")
    return text


def get_text_from_image_file(img_file):
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    enhance_file_object = graphics.enhance_contrast_from_source_file(
        img_file=img_file
    )
    img = Image.fromarray(enhance_file_object)
    text = pytesseract.image_to_string(img, lang="vie+eng")
    return text


def get_text_from_image_file_with_all_channels(img_file):
    img = cv2.imread(img_file)
    b, g, r = cv2.split(img)

    text_b = pytesseract.image_to_string(b, lang="vie+eng")
    text_g = pytesseract.image_to_string(g, lang="vie+eng")
    text_r = pytesseract.image_to_string(b, lang="vie+eng")
    return text_b, text_g, text_r
