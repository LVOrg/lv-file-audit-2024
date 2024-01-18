import hashlib
import json
import os.path
import typing

import PIL
import numpy
import numpy as np
import easyocr
import cv2
from deskew import determine_skew
import math
from skimage.transform import rotate
from skimage import transform,io

__reader__ = None


def get_skew(img_src: typing.Union[str, np.ndarray, PIL.Image.Image]) -> typing.Optional[float]:
    if isinstance(img_src, str):
        if not os.path.isfile(img_src):
            raise FileNotFoundError(f"{img_src} was not found")
        image = cv2.imread(img_src)
    elif isinstance(img_src, np.ndarray):
        image = img_src
    elif isinstance(img_src, PIL.Image.Image):
        image = np.array(img_src)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    if angle:
        angle = float(angle)
    return angle


def rotate(
        image_src: typing.Union[str, np.ndarray, PIL.Image.Image],
        angle: float,
        background: typing.Union[int, typing.Tuple[int, int, int]]
) -> np.ndarray:
    if isinstance(image_src, str):
        image = cv2.imread(image_src)
    elif isinstance(image_src, np.ndarray):
        image = image_src
    elif isinstance(image_src, PIL.Image.Image):
        image = np.array(image_src)
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


def get_all_rectangles(msg_src: str, model_storage_directory: str, cache_dir: str) -> typing.Tuple[typing.List[
    typing.List[typing.List[numpy.int64]]], easyocr.Reader]:
    global __reader__
    if __reader__ is None:
        __reader__ = easyocr.Reader(['vi'], model_storage_directory=model_storage_directory, gpu=False)

    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    with open(msg_src, "rb") as f:
        data = f.read()
        hash = hashlib.sha256(data).hexdigest()
        json_data_file = os.path.join(cache_dir, hash + ".json")
        if os.path.isfile(json_data_file):
            try:
                with open(json_data_file, "rb") as fs:
                    data = json.loads(fs.read().decode('utf8'))
                return data
            except:
                pass

    ret = __reader__.readtext(msg_src)

    data = [(
        (int(max(x[0][0][0],0)), int(max(x[0][0][1],0))),
        (int(max(x[0][1][0],0)), int(max(x[0][1][1],0))),
        (int(max(x[0][2][0],0)), int(max(x[0][2][1],0))),
        (int(max(x[0][3][0],0)), int(max(x[0][3][1],0))))
        for x in ret]
    json_data_file = os.path.join(cache_dir, hash + ".json")
    with open(json_data_file, "wb") as fs:
        fs.write(json.dumps(data).encode('utf8'))

    return data
