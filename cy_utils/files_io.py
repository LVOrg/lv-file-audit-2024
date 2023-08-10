"""
The library is use for save or load any numpy.ndarray
"""
import os.path

import numpy
import numpy as np
from PIL import Image
import cv2
import pathlib


def load_image(src_file: str,is_grayscale = False) -> numpy.ndarray:
    """
    Use open cv load file into numpy.ndarray
    :param is_grayscale: if True load as black-white image regardless source color file
    :param src_file:
    :return:
    """
    if is_grayscale:
        ret = cv2.imread(src_file,0)
        return ret
    else:
        ret = cv2.imread(src_file)
        return ret


def save(image: numpy.ndarray, to_file: str):
    """
    Save numpy.ndarray to file
    :param image:
    :param to_file:
    :return:
    """
    dir = pathlib.Path(to_file).parent.__str__()
    if not os.path.isdir(dir):
        os.makedirs(dir, exist_ok=True)
    im = Image.fromarray(image)
    im.save(to_file)
