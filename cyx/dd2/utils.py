import hashlib
import os
import uuid
from PIL import Image
import  numpy  as np
if not os.environ.get("DEEPDOCTECTION_CACHE"):
    raise Exception(f"Please set DEEPDOCTECTION_CACHE path")
else:
    if not os.path.isdir(os.environ.get("DEEPDOCTECTION_CACHE")):
        os.makedirs(os.environ.get("DEEPDOCTECTION_CACHE"),exist_ok=True)

import os.path

import img2pdf

__analyzer__ = None

from deepdoctection.pipe.doctectionpipe import DoctectionPipe


def __get_analyzer__() -> DoctectionPipe:
    global __analyzer__
    if __analyzer__ is None:
        __analyzer__ = dd.get_dd_analyzer(reset_config_file=True)
    return __analyzer__


import deepdoctection as dd

def pixels_to_points(pixel_value, dpi):
    """Converts a pixel value to points based on the given DPI.

    Args:
        pixel_value (int or float): The pixel value to convert.
        dpi (int or float): The DPI (dots per inch) of the image or context.

    Returns:
        float: The corresponding point value.
    """

    points_per_inch = 72  # Number of points per inch
    pixels_per_inch = dpi  # Number of pixels per inch
    points_per_pixel = points_per_inch / pixels_per_inch
    return int(pixel_value * points_per_pixel)
def __get_has_content_file__(img_src: str):
    with open(img_src, "rb") as f:
        data = f.read()
        hash = hashlib.sha256(data).hexdigest()
        return hash


def convert_image_to_pdf(img_src: str, out_put_pdf: str):
    with open(out_put_pdf, "wb") as f:
        f.write(img2pdf.convert([img_src]))


def predict_image(img_src: str, tmp_dir: str):
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)
    process_dir_name= __get_has_content_file__(img_src)
    process_dir = os.path.join(tmp_dir,process_dir_name)
    if not os.path.isdir(process_dir):
        os.makedirs(process_dir,exist_ok=True)
    file_name = "image.pdf"

    out_put_pdf_file = os.path.join(process_dir, file_name)
    convert_image_to_pdf(img_src,out_put_pdf_file)
    analyzer = __get_analyzer__()
    df = analyzer.analyze(path=out_put_pdf_file)
    df.reset_state()  # Trigger some initialization
    doc = iter(df)
    page_index=0
    boxes = []
    for x in doc:
        boxes += [
            (   int(a.bounding_box.ulx),            #x1
                int(a.bounding_box.uly),            #y1
                int(a.bounding_box.lrx),            #x2
                int(a.bounding_box.lry)             #y2

            )
            for a in x.annotations if a.relationships!={}
        ]
        for table in x.tables:
            print(table)
        image = x.viz()
        track_file_name = f"track_{page_index:04d}.png"
        image_pil = Image.fromarray(image.astype(np.uint8))
        image_pil.save(os.path.join(process_dir,track_file_name))
        page_index+=1
    crop_id=0
    image = Image.open(img_src)
    # Convert the image to a NumPy array
    image_array = np.array(image)
    dpiy,dpix = image.info.get("dpi")
    for x1,y1,x2,y2 in boxes:
        x1,y1,x2,y2=pixels_to_points(x1,dpix),pixels_to_points(y1,dpiy),pixels_to_points(x2,dpix),pixels_to_points(y2,dpiy)
        cropped_image = image_array[y1:y2, x1:x2]
        image_pil = Image.fromarray(cropped_image.astype(np.uint8))
        image_pil.save(os.path.join(process_dir, f"crop_{crop_id}.png"))
        crop_id+=1
