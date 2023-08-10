import os.path
import pathlib
import shutil

from cy_utils import graphics, files_io, set_temp_dir, __verify_temp_dir__, new_temp_dir, new_temp_file

import numpy

from PIL import Image

import img2pdf


def save_to_pdf(img_obj: numpy.ndarray, to_pdf_file):
    """
    Save numpy.ndarray to pdf file
    :param img_obj:
    :param to_pdf_file:
    :return:
    """
    __verify_temp_dir__()
    im = Image.fromarray(img_obj)
    tem_image_file = new_temp_file("png")
    im.save(tem_image_file)
    pdf_bytes = img2pdf.convert(tem_image_file)
    dir = pathlib.Path(to_pdf_file).parent.__str__()
    if not os.path.isdir(dir):
        os.makedirs(dir)
    with open(to_pdf_file, "wb") as file:
        file.write(pdf_bytes)
        file.close()
        del pdf_bytes
    os.remove(tem_image_file)
    return to_pdf_file


def gray_scale_enhance_image_to_pdf(img_file: str, to_pdf_file: str):
    original_image = files_io.load_image(img_file)
    grayscale_image = graphics.gray_scale(original_image)
    enhance_contrast_of_gray_scale = graphics.enhance_contrast(
        original_image=original_image,
        gray_scale_img=grayscale_image
    )
    enhance_contrast_of_gray_scale_bin = graphics.gray_scale_to_binary(original_image)
    save_to_pdf(
        img_obj=enhance_contrast_of_gray_scale_bin,
        to_pdf_file=to_pdf_file
    )
    return None
