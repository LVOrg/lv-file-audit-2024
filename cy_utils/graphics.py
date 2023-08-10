import typing

import numpy
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from cy_utils import files_io


def gray_scale(img: numpy.ndarray):
    """
    Use open cv grayscale an image in numpy.ndarray
    The chanel of image will be reduced
    :param img:
    :return:
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray


def enhance_contrast(original_image: numpy.ndarray, gray_scale_img: numpy.ndarray,
                     factor: float = 0.3) -> numpy.ndarray:
    """
    Compare between original image and grayscale image to make a better contrast
    Note: dark region maybe fill all by black color
    :param original_image:
    :param gray_scale_img:
    :param factor:
    :return:
    """
    img = Image.fromarray(original_image)
    enhancer = ImageEnhance.Sharpness(img).enhance(factor)
    if gray_scale_img.std() < 30:
        enhancer = ImageEnhance.Contrast(enhancer).enhance(factor)
    return np.array(enhancer)


def gray_scale_to_binary(gray_scale_img: numpy.ndarray, invert_color: bool = False) -> numpy.ndarray:
    """
    The method will fulfill all channels to grayscale image, so it could be use as an image with full info
    :param invert_color:
    :param gray_scale_img:
    :return:
    """
    gray = cv2.cvtColor(gray_scale_img, cv2.COLOR_BGR2GRAY)
    if invert_color:
        thresh, img_bin = cv2.threshold(
            gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        img_bin = 255 - img_bin
        return img_bin
    else:
        thresh, img_bin = cv2.threshold(
            gray, 255, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return img_bin


def enhance_contrast_from_source_file(img_file, invert_color: bool = False) -> numpy.ndarray:
    """
    Enhance contrast from file return numpy.ndarray of file
    :param img_file:
    :return:
    """
    original_image = files_io.load_image(img_file)
    grayscale_image = gray_scale(original_image)
    enhance_contrast_of_gray_scale = enhance_contrast(
        original_image=original_image,
        gray_scale_img=grayscale_image
    )
    enhance_contrast_of_gray_scale_bin = gray_scale_to_binary(original_image, invert_color)
    return enhance_contrast_of_gray_scale_bin


def draw_lines(img: numpy.ndarray, lines: numpy.ndarray, fill_color=(0, 0, 255), thickness=3):
    """
    The method will draw lines to image
    :param img:
    :param lines:
    :param fill_color:
    :param thickness:
    :return:
    """
    for l in lines:
        if l.__len__() == 1:
            c = l[0]
            x1, y1, x2, y2 = tuple(c)
            cv2.line(img, (x1, y1), (x2, y2), fill_color, thickness=thickness)
        else:

            x1, y1, x2, y2 = tuple(l)
            cv2.line(img, (x1, y1), (x2, y2), fill_color, thickness=thickness)
    return img


def draw_lines_in_blank(img: numpy.ndarray, lines, fill_color=(0, 0, 255), thickness=3):
    """
    Make a new blank image with the same size of input image and draw lines in new image
    :param img:
    :param lines:
    :param fill_color:
    :param thickness:
    :return:
    """
    image = np.zeros(img.shape, np.uint8)
    for l in lines:
        c = l[0]
        x1, y1, x2, y2 = tuple(c)
        cv2.line(image, (x1, y1), (x2, y2), fill_color, thickness=thickness)
    return image


def draw_poly_line(image: numpy.ndarray, points, color=(0, 0, 255), thickness=3):
    if isinstance(points, numpy.ndarray):
        image = cv2.polylines(image, [points],
                              True, color, thickness)
        return image
    else:
        pts = np.array(points, np.int32)
        image = cv2.polylines(image, [pts],
                              True, color, thickness)
        return image
