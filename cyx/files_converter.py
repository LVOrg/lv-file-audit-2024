import img2pdf
from PIL import Image
import os
import pathlib
def convert_file_ext(file_path,ext):
    dir = pathlib.Path(file_path).parent.__str__()
    file_name = pathlib.Path(file_path).stem
    ret = os.path.abspath(
        os.path.join(dir,file_name+"."+ext)
    )
    return ret

def convert_image_to_pdf(image_path, pdf_path):
    pdf = img2pdf.convert(image_path)
    with open(pdf_path, "wb") as f:
        f.write(pdf)
