import os
import pathlib
import shutil
import typing
import uuid

import numpy
import numpy as np
import cv2
import math
import pytesseract
from PIL import Image
import pdf2image
import img2pdf
from matplotlib import pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfMerger
import PyPDF2.errors


def wrappe_paper(img: numpy.ndarray, padding=20):
    # H, W, D = img.shape
    #
    # show_image(img)
    # ret_img = np.zeros((H+padding, W+padding, D), dtype = np.uint8)
    #
    # ret_img = np.concatenate((img,ret_img), axis=2)
    # show_image(ret_img)
    # return ret_img
    old_image_height, old_image_width, channels = img.shape

    # create new image of desired size and color (blue) for padding
    new_image_width = old_image_width + padding
    new_image_height = old_image_height + padding
    color = (255, 255, 255)
    result = np.full((new_image_height, new_image_width, channels), color, dtype=np.uint8)

    # compute center offset
    x_center = (new_image_width - old_image_width) // 2
    y_center = (new_image_height - old_image_height) // 2

    # copy img image into center of result image
    result[y_center:y_center + old_image_height, x_center:x_center + old_image_width] = img

    return result


class MediaAngleInfo:
    angle: float
    upside_down_able: bool
    orientation: int
    image_to_osd_error: bool
    skew: float
    median_angle: float

    def __init__(self, orientation: int, median_angle: float, skew: float, upside_down_able: bool, angle: float,
                 image_to_osd_error: bool):
        self.upside_down_able = upside_down_able
        self.median_angle = median_angle
        self.angle = angle
        self.skew = skew
        self.orientation = orientation
        self.image_to_osd_error = image_to_osd_error


def __calculate_if_ocr_osd_is_success__(ref_file_path: str, print_info, skew, median_angle, orientation,
                                        image_to_osd_error):
    _skew, _median_angle = math.ceil(skew), math.floor(median_angle)
    _r_skew, _r_median_angle = round(skew), round(median_angle)
    assert isinstance(ref_file_path, str)
    if orientation == 180 and skew == -90.0 and median_angle == -90.0:
        print(
            f"{ref_file_path} orientation==180 and skew== -90.0 and median_angle== -90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and round(skew, 1) < 0 and round(skew, 1) > -1.0 and median_angle == -90.0:
        print(
            f"{ref_file_path} orientation == 0 and (-90-round(skew, 0)==round(median_angle,0))")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=skew,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and round(-90 - skew, 1) < 0 and round(-90 - skew, 1) > -3.0 and median_angle == -90.0:
        print(
            f"{ref_file_path} orientation == 0 and round(-90-skew, 1) <0  and round(-90-skew, 1)>-3.0 and median_angle == -90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=(-90 - skew),
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and round(skew, 0) == 0 and median_angle == -90.0:
        print(
            f"{ref_file_path} orientation == 0 and round(skew, 0) ==0 and median_angle == -90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=skew,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and (-90 - round(skew, 0) == round(median_angle, 0) and median_angle == -90.0):
        print(
            f"{ref_file_path} orientation == 0 and (-90-round(skew, 0)==round(median_angle,0) and median_angle==-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-90.0 - skew,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and (round(-90 - skew, 0) == round(median_angle, 0) and median_angle != -90.0):
        print(
            f"{ref_file_path} orientation == 0 and (round(-90-skew, 0)==round(median_angle,0) and median_angle!=-90.0)")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-90 - skew,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )

    if orientation == 0 and (round(skew, 0) <= -90 or round(skew, 0) >= -89.0) and math.ceil(median_angle) == 90.0:
        print(
            f"{ref_file_path} orientation == 0 and (round(skew, 0) <= -90 or round(skew, 0)>= -89.0) and math.ceil(median_angle) == 90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=(90 - median_angle),
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and round(skew, 0) == -90 and median_angle == -90.0:
        print(f"{ref_file_path} orientation==0 and round(skew,0)==-90 and median_angle == -90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and round(skew, 0) == -90.0 and median_angle == 0.0:
        print(f"{ref_file_path} orientation == 0 and round(skew,0)==-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew < 0 and median_angle == 0.0:
        print(f"{ref_file_path} orientation == 0 and skew<0 and median_angle == 0.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-1 * min(abs(median_angle), abs(skew)),
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )

    if orientation == 0 and round(skew, 0) == -90.0 and median_angle == 0.0:
        print(f"{ref_file_path} orientation==0 and round(skew,0)==-90.0 and median_angle ==0.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew == 0.0 and median_angle == -90.0:
        print(f"{ref_file_path} orientation == 0 and skew == 0.0 and median_angle == -90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew == -90.0 and median_angle == -90.0:
        print(f"{ref_file_path} orientation==0 and skew==-90.0 and median_angle==-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 270 and skew == 0.0 and median_angle == -90.0:
        print(f"{ref_file_path} orientation==270 and skew==0.0 and median_angle==-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=90,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew < 0 and median_angle > 0:
        print(f"{ref_file_path} orientation==0 and skew<0 and median_angle>0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-1 * median_angle,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew < 0 and median_angle < 0 and median_angle != -90.0:
        print(f"{ref_file_path} orientation == 0 and skew < 0 and median_angle < 0 and median_angle!=-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=median_angle - min(median_angle, skew),
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew == 0.0 and median_angle > 0:
        print(f"{ref_file_path} orientation==0 and skew==0.0 and median_angle>0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-1 * median_angle,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 90 and skew == -90.0 and median_angle == -90.0:
        print(f"{ref_file_path} orientation==90 and skew==-90.0 and median_angle==-90.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=90,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 90 and skew == -90.0 and median_angle == 0.0:
        print(f"{ref_file_path} orientation==90 and skew==-90.0 and median_angle==0.0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 180 and skew == -90.0 and median_angle == 0:
        print(f"{ref_file_path} orientation==180 and skew==-90.0 and median_angle==0")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and skew == 0.0 and median_angle == 0.0:
        print(f"{ref_file_path} 0 degree angle")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )

    if orientation == 180 and skew == 0.0 and median_angle == 0.0:
        """
        Case 0
        """

        print(f"{ref_file_path} 180 degree angle")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=180,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if orientation == 0 and _skew == -90 and _median_angle == -90:
        """
        Case 0
        """

        print(f"{ref_file_path} 90 degree angle")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=90,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )


    elif orientation == 0 and _skew * _median_angle > 0:
        """
            -Skew angle = -85.89612579345703
            -Median angle = -9.990098340342508
            -Orientation = 0
        """
        if median_angle < 0:
            print(f"{ref_file_path} case 0.2")
            print_info(orientation, median_angle, skew, True)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=True

            )


        else:
            print(f"{ref_file_path} case 0.2 upside down")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )

        """"
        -Skew angle = -85.89612579345703
    -Median angle = -9.990098340342508
    -Orientation = 0
        """
        """
        -Skew angle = -85.89612579345703
    -Median angle = -9.991833575998513
    -Orientation = 0
        """
    elif orientation == 0 and _skew * _median_angle < 0:
        delta = round(median_angle - skew, 3)
        if delta < 90:
            print(f"{ref_file_path} case 0.3")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )


        else:
            print(f"{ref_file_path} case 0.3 upside down")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )

    elif orientation == 0 and skew == -90.0 and median_angle == 0.0:
        """
        upside down
        """
        print(f"{ref_file_path} upside down")
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    elif orientation == 270 and skew == -90.0 and median_angle == -90.0:
        print(f"{ref_file_path} case 90 rotation")
        return MediaAngleInfo(
            angle=90,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    elif orientation == 270 and _skew * _median_angle > 0:
        delta = abs(round(skew + median_angle, 3))
        if delta >= 90:
            print(f"{ref_file_path} case 270 clockwise over 90")
            print(f'-\tdelta={delta}\n')
            print_info(orientation, median_angle, skew, True)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=True

            )
        else:
            print(f"{ref_file_path} case 270 clockwise limit 90")
            print_info(orientation, median_angle, skew, True)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=True

            )
    elif orientation == 270 and _skew == -1 * _median_angle:
        print(f"{ref_file_path} case 270 not clock wise opposite")
        print_info(orientation, median_angle, skew, False)
        return MediaAngleInfo(
            angle=-1 * median_angle,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    elif orientation == 270 and _skew * _median_angle < 0:

        delta = round(median_angle - skew, 3)

        if delta <= 90:

            print(f"{ref_file_path} case 270 not clock wise below 90")
            print(f"\tdetal={delta}")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
        else:
            print(f"{ref_file_path} case 270 not clock wise over 90")
            print(f"\tdetal={delta}")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
    elif orientation == 180 and skew * median_angle < 0:

        delta = round(median_angle - skew, 3)

        if delta < 135:
            print(f"{ref_file_path} case orientation==180  clockwise over 90")
            print(f"\t-delta={delta}")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=True

            )
        else:
            print(f"{ref_file_path} case orientation==180  clockwise below 90")
            print(f"\t-delta={delta}")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
    elif orientation == 180 and skew * median_angle > 0:
        delta = round(_skew - _median_angle, 3)
        if delta <= 90:
            print(f"{ref_file_path} case orientation==180  clockwise reverse below 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
        else:
            print(f"{ref_file_path} case orientation==180  clockwise reverse over 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
    elif orientation == 90 and skew * median_angle > 0:
        delta = round(median_angle - skew, 3)
        if delta > 90:
            print(f"{ref_file_path} case orientation==90  clockwise  over 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
        else:
            print(f"{ref_file_path} case orientation==90  clockwise  below 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
    elif orientation == 90 and skew * median_angle < 0:
        delta = round(median_angle - skew, 3)
        if delta < 90:
            print(f"{ref_file_path} case orientation==90  clockwise reverse below 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )
        else:
            print(f"{ref_file_path} case orientation==90  clockwise reverse over 90")
            print_info(orientation, median_angle, skew, False)
            return MediaAngleInfo(
                angle=-1 * median_angle + 180,
                median_angle=median_angle,
                skew=skew,
                orientation=orientation,
                image_to_osd_error=image_to_osd_error,
                upside_down_able=False

            )


def __calculate_if_ocr_osd_is_fail__(ref_file_path: str, print_info, skew, median_angle, orientation,
                                     image_to_osd_error):
    print_info(orientation, median_angle, skew, False)
    if orientation == 0 and skew == -90.0 and median_angle == 0:
        print(f"{ref_file_path}, image_to_osd_error orientation==0 and skew== -90.0 and median_angle ==0")
        return MediaAngleInfo(
            angle=0,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    if abs(skew) > 45:
        print(f"{ref_file_path}, image_to_osd_error abs(skew)>45")
        return MediaAngleInfo(
            angle=median_angle + 90,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )
    else:
        print(f"{ref_file_path}, image_to_osd_error default")
        return MediaAngleInfo(
            angle=median_angle,
            median_angle=median_angle,
            skew=skew,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error,
            upside_down_able=False

        )


def get_median_angle(img: numpy.ndarray, ref_file_path: str = None, lang="osd") -> MediaAngleInfo:
    """
    Exactly detect document if it rota any angle. Even up-side-down text content and vertical flip
    :param img_before:
    :return:
    """

    def print_info(orientation, median_angle, skew, maybe_upside_down: bool):
        print(f"\t-Skew angle = {skew}")
        print(f"\t-Median angle = {median_angle}")
        print(f"\t-Orientation = {orientation}")
        print(f"\tMaybe upside down={maybe_upside_down}")

    img_before = img
    img_gray = cv2.cvtColor(img_before, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []

    for x1, y1, x2, y2 in lines[0]:
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    median_angle = np.median(angles)
    """
    Still glitch
    """
    # a_90 = detect_90_rota(img_before)
    orientation = 0
    image_to_osd_error = False
    try:
        data = pytesseract.image_to_osd(img_before, output_type=pytesseract.Output.DICT, lang=lang)
        orientation = data.get("orientation", 0)
    except pytesseract.pytesseract.TesseractError as e:
        print("Warning error:\n")
        print(e)
        print(ref_file_path)
        image_to_osd_error = True
        orientation = 0
    skew = getSkewAngle(cvImage=img_before)
    if not image_to_osd_error:
        result = __calculate_if_ocr_osd_is_success__(
            ref_file_path=ref_file_path,
            print_info=print_info,
            skew=skew,
            median_angle=median_angle,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error
        )
        if result is not None:
            return result
        else:
            print("Not impletement:\n")
            print_info(orientation, median_angle, skew, False)

            raise Exception("Not impletement")
    elif image_to_osd_error:
        result = __calculate_if_ocr_osd_is_fail__(
            ref_file_path=ref_file_path,
            print_info=print_info,
            skew=skew,
            median_angle=median_angle,
            orientation=orientation,
            image_to_osd_error=image_to_osd_error
        )
        if result is not None:
            return result
        else:
            print("Not impletement:\n")
            print_info(orientation, median_angle, skew, False)

    # elif image_to_osd_error and orientation == 0 and skew == 0 and median_angle > 0:
    #     print(f"{ref_file_path} case oorientation==0 and skew==0 and median_angle>0")
    #     print_info(orientation, median_angle, skew, False)
    #     return MediaAngleInfo(
    #         angle=-1 * median_angle,
    #         median_angle=median_angle,
    #         skew=skew,
    #         orientation=orientation,
    #         image_to_osd_error=image_to_osd_error,
    #         upside_down_able=False
    #
    #     )
    # elif image_to_osd_error and orientation == 0 and skew == 0 and median_angle < 0:
    #     print(f"{ref_file_path} case oorientation==0 and skew==0 and median_angle<0")
    #     print_info(orientation, median_angle, skew, False)
    #     return MediaAngleInfo(
    #         angle=-1 * median_angle,
    #         median_angle=median_angle,
    #         skew=skew,
    #         orientation=orientation,
    #         image_to_osd_error=image_to_osd_error,
    #         upside_down_able=False
    #
    #     )
    else:
        print("Not impletement:\n")
        print_info(orientation, median_angle, skew, False)

        raise Exception("Not impletement")

    if ref_file_path:
        print(f"file='{ref_file_path}:'\n")
        print_info()

    """
        -Skew angle = -90.0
        -Median angle = -90.0
        -Orientation = 0
	    no rotation
    """
    """
        -Skew angle = 0.0
        -Median angle = 0.0
        -Orientation = 0
        no rotation
    """
    """
        -Skew angle = -90.0
        -Median angle = -0.7345210342548154
        -Orientation = 0
        return Median angle
    """
    """
        -Skew angle = -90.0
	    -Median angle = 0.8550973962667232
	    -Orientation = 0
	    return Median angle
    """
    """
        -Skew angle = -0.0
        -Median angle = -90.0
        -Orientation = 0
        return Median angle+Skew angle+90+Orientation
    """
    # if skew==-90 and median_angle==0:
    #     return 0
    # elif skew==-90 and median_angle!=0:
    #     return -1 * median_angle
    # # else:
    # #     return -1 * median_angle
    # elif skew < -90:
    #     return 270 - median_angle
    # else:
    #     return -1 * median_angle

    return median_angle


def getSkewAngle(cvImage: numpy.ndarray) -> float:
    """
    Just deskskew some angle rotation can not detect. Such as: up-side-down text content or vertical flip
    :param cvImage:
    :return:
    """

    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)
    del newImage
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


def rotate_image(mat: numpy.ndarray, angle: float):
    """
    Rota image fron center of image with angle
    :param mat:
    :param angle:
    :return:
    """
    # import imutils
    # result = imutils.rotate(image, angle)
    # # image_center = tuple(np.array(image.shape[1::-1]) / 2)
    # # H,W,D= image.shape
    # # image_center=(image.shape)
    # # rot_mat = cv2.getRotationMatrix2D((H/2,W/2), angle, 1.0)
    # # result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    # return result
    """
        Rotates an image (angle in degrees) and expands image to avoid cropping
        """

    height, width = mat.shape[:2]  # image shape has 3 dimensions
    image_center = (
        width / 2,
        height / 2)  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h), borderValue=(255, 255, 255))
    return rotated_mat


def show_image(image: numpy.ndarray, title="unknown"):
    cv2.imshow(title, image)
    cv2.waitKey(0)


def detect_90_rota(image):
    mask = np.zeros(image.shape, dtype=np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    adaptive = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 4)

    cnts = cv2.findContours(adaptive, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        area = cv2.contourArea(c)
        if area < 45000 and area > 20:
            cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    h, w = mask.shape
    cv2.imshow("mask", mask)
    cv2.waitKey(0)

    # Horizontal
    if w > h:
        left = mask[0:h, 0:0 + w // 2]
        right = mask[0:h, w // 2:]
        left_pixels = cv2.countNonZero(left)
        right_pixels = cv2.countNonZero(right)
        return 0 if left_pixels >= right_pixels else 180
    # Vertical
    else:
        top = mask[0:h // 2, 0:w]
        bottom = mask[h // 2:, 0:w]
        top_pixels = cv2.countNonZero(top)
        bottom_pixels = cv2.countNonZero(bottom)
        return 90 if bottom_pixels >= top_pixels else 270


def align_image(source_file: str, dest_file: str, create_backup_old=True, skip_if_output_is_exist=False):
    if skip_if_output_is_exist:
        if os.path.isfile(dest_file):
            return
    image = cv2.imread(source_file)

    # image = wrappe_paper(image)
    _, file_ext = os.path.splitext(source_file)
    backup_path = os.path.join(pathlib.Path(dest_file).parent.__str__(),
                               f"{pathlib.Path(dest_file).stem}.original{file_ext}")
    median_info = get_median_angle(image, ref_file_path=source_file)
    cv2.imwrite(backup_path, image)

    image = rotate_image(image, median_info.angle * (-1))
    cv2.imwrite(dest_file, image)


def rota_image_file(src: str, dest_dir: str, angle: float, index: int) -> str:
    str_index = f"{index}"
    dest_file = os.path.join(dest_dir, f"{pathlib.Path(src).stem}_{str_index}{os.path.splitext(src)[1]}")
    image = cv2.imread(src)
    image = rotate_image(image, angle)
    cv2.imwrite(dest_file, image)
    return dest_file


TEMP_DIR = None


def set_temp_dir(dir: str):
    if not os.path.isdir(dir):
        os.makedirs(dir, exist_ok=True)
    global TEMP_DIR
    TEMP_DIR = dir


def do_deskew(src: str, dest: str) -> str:
    if TEMP_DIR is None:
        raise Exception("It looks like thou forgot set TEMP_DIR, please call set_temp_dir")
    dest_dir = pathlib.Path(dest).parent.__str__()
    tem_process_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    if not os.path.isdir(tem_process_dir):
        os.makedirs(tem_process_dir, exist_ok=True)
    dest_file = os.path.join(tem_process_dir, pathlib.Path(dest).name)
    image = cv2.imread(src)
    median_info = get_median_angle(image, ref_file_path=src)
    image = rotate_image(image, median_info.angle * (-1))
    cv2.imwrite(dest_file, image)
    shutil.move(dest_file, dest_dir)
    shutil.rmtree(tem_process_dir)

    return dest


def scale_img(src: str, des: str, max_width: int) -> str:
    im = Image.open(src)
    if max_width is None:
        im.save(des)
        im.close()
        del im
        return des
    w, h = im.size
    # if w<max_width:
    #     return src
    rate = max_width / w
    _w, _h = int(w * rate), int(h * rate)
    im_resized = im.resize((_w, _h), Image.ANTIALIAS)
    im_resized.save(des)
    im.close()
    del im
    return des


SCALE_SIZE_A0_300_DPI = 9933
SCALE_SIZE_A0_72_DPI = 2384

SCALE_SIZE_A1_300_DPI = 7016
SCALE_SIZE_A1_72_DPI = 1684

SCALE_SIZE_A4_300_DPI = 2480
SCALE_SIZE_A4_72_DPI = 595

SCALE_SIZE_A5_300_DPI = 1748
SCALE_SIZE_A5_72_DPI = 420

SCALE_SIZE_A6_300_DPI = 1240
SCALE_SIZE_A6_72_DPI = 298

SCALE_SIZE_A7_300_DPI = 874
SCALE_SIZE_A7_72_DPI = 210
from  PIL import ImageEnhance
def gray_scale(img: numpy.ndarray):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray
def save_use_cv2(image:numpy.ndarray, to_file:str):

    im = Image.fromarray(image)
    im.save(to_file)
def load_image_use_cv2(src_file: str,is_gray_scale=False) -> numpy.ndarray:
    if is_gray_scale:
        ret = cv2.imread(src_file,0)
        return ret

    ret = cv2.imread(src_file)
    return ret
def enhance_contrast(original_image:numpy.ndarray, gray_scale_img: numpy.ndarray, factor: float = 0.3) -> numpy.ndarray:
    img = Image.fromarray(original_image)
    enhancer = ImageEnhance.Sharpness(img).enhance(factor)
    if gray_scale_img.std() < 30:
        enhancer = ImageEnhance.Contrast(enhancer).enhance(factor)
    return np.array(enhancer)

def gray_scale_add_chanels(gray_scale_img: numpy.ndarray) -> numpy.ndarray:
    thresh, img_bin = cv2.threshold(
        gray_scale_img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # img_bin = 255 - img_bin
    return img_bin
def gray_scale_to_binary(gray_scale_img: numpy.ndarray) -> numpy.ndarray:
    gray = cv2.cvtColor(gray_scale_img, cv2.COLOR_BGR2GRAY)
    thresh, img_bin = cv2.threshold(
        gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # img_bin = 255 - img_bin
    return img_bin

def verify_file_for_deepdoctection(src_of_pdf_or_image: str, image_scale_size: float = 705, pdf_scale_size=720) -> \
typing.List[str]:
    from PIL import Image

    scale_size = image_scale_size
    if os.path.splitext(src_of_pdf_or_image.lower())[1] == ".pdf":
        scale_size = pdf_scale_size
    else:
        im = Image.open(src_of_pdf_or_image)
        # print(f"{src_of_pdf_or_image} has dpi ={im.info['dpi']}")
    print(f"{src_of_pdf_or_image} will scale to {scale_size}")
    if TEMP_DIR is None:
        raise Exception("It looks like thou forgot set TEMP_DIR, please call set_temp_dir")
    tem_process_dir = os.path.join(TEMP_DIR, str(uuid.uuid4()))
    if not os.path.isdir(tem_process_dir):
        os.makedirs(tem_process_dir)
    if os.path.splitext(src_of_pdf_or_image)[1] == ".pdf":
        """
        Clear all text and convert to image
        """
        pages = pdf2image.convert_from_path(src_of_pdf_or_image)
        index = 0
        new_output_pdf = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}.deskew.pdf")
        pdfs = []

        for page in pages:
            output_image = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].png")
            output_image_gray_scale = os.path.join(tem_process_dir,
                                                   f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].gray_scale.png")
            output_pdf = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].pdf")
            output_image_deskew = os.path.join(tem_process_dir,
                                               f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].deskew.png")
            output_image_deskew_A4 = os.path.join(tem_process_dir,
                                                  f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].deskew.A4.png")
            output_image_deskew_310 = os.path.join(tem_process_dir,
                                                   f"{pathlib.Path(src_of_pdf_or_image).stem}_[{index}].deskew.310_dpi.png")

            page.save(output_image, 'PNG')
            og_image = load_image_use_cv2(output_image)
            gray_image = gray_scale(og_image)
            gray_image_enhance = enhance_contrast(og_image,gray_image)
            gray_image_enhance_bin = gray_scale_to_binary(gray_image_enhance)
            save_use_cv2(gray_image_enhance_bin,output_image_gray_scale)
            del og_image
            del gray_image
            del gray_image_enhance
            del gray_image_enhance_bin




            scale_img(output_image_gray_scale, output_image_deskew_A4, pdf_scale_size)  # 300 dpi A3
            # plt.savefig('DR.png', dpi=310)
            # deskew_file = do_deskew(output_image, output_image_deskew)
            deskew_file = do_deskew(output_image_deskew_A4, output_image_deskew)
            # image = cv2.imread(output_image,output_image_deskew)
            load_file=output_image_deskew
            print(f"{load_file} save to pdf")
            with Image.open(load_file, mode="r") as img:
                pdf_bytes = img2pdf.convert(img.filename)
                with open(output_pdf, "wb") as file:
                    file.write(pdf_bytes)
                    file.close()
                    del pdf_bytes
            pdfs += [output_pdf]
            index += 1
            # image.close()

        return pdfs
    from  cyx import cv2_utils
    # image = Image.open(src)
    _des = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}.pdf")
    output_image_gray_scale = os.path.join(tem_process_dir,
                                           f"{pathlib.Path(src_of_pdf_or_image).stem}.gray_scale.png")
    output_image_deskew = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}.deskew.png")
    output_image_deskew_A4 = os.path.join(tem_process_dir, f"{pathlib.Path(src_of_pdf_or_image).stem}.deskew.{image_scale_size}.png")
    og_image = load_image_use_cv2(src_of_pdf_or_image)

    gray_image = gray_scale(og_image)
    gray_image_enhance = enhance_contrast(og_image, gray_image)
    gray_image_enhance_bin = gray_scale_to_binary(gray_image_enhance)
    save_use_cv2(gray_image_enhance_bin, output_image_gray_scale)
    # gray_image_enhance_bin = gray_scale_add_chanels(og_image)
    # save_use_cv2(gray_image_enhance_bin, output_image_gray_scale)
    del og_image
    del gray_image
    del gray_image_enhance
    del gray_image_enhance_bin
    # deskew_file = do_deskew(src_of_pdf_or_image, output_image_deskew)
    scale_img(output_image_gray_scale, output_image_deskew_A4,image_scale_size) # scale_size)
    load_file = output_image_deskew_A4
    print(f"Save {load_file} to pdf")
    with Image.open(load_file, mode="r") as img:
        pdf_bytes = img2pdf.convert(img.filename)
        with open(_des, "wb") as file:
            file.write(pdf_bytes)
            file.close()

    return [_des]


DATA_SET_CACH_DIR = None
deepdoctection_analyzer = None


def set_dataset_cache_dir(path: str):
    global DATA_SET_CACH_DIR
    DATA_SET_CACH_DIR = path
    os.environ["XDG_CACHE_HOME"] = DATA_SET_CACH_DIR
    os.environ["DOCTR_CACHE_DIR"]= DATA_SET_CACH_DIR


def extract_html_from_pdf(pdf_file: str):
    global DATA_SET_CACH_DIR
    if DATA_SET_CACH_DIR is None:
        raise Exception("Please call ")

    import deepdoctection as dd
    global deepdoctection_analyzer
    if deepdoctection_analyzer is None:
        deepdoctection_analyzer = dd.get_dd_analyzer(
            language="vie+eng"
        )
    df = deepdoctection_analyzer.analyze(path=pdf_file)  # setting up pipeline
    tx = df.reset_state()  # Trigger some initialization

    doc = iter(df)
    pages = list(doc)

    for page in pages:
        print(page.text)
        if page.tables.__len__() > 0:
            print("====================== tables ===============================")

            for x in page.tables:
                print(x.html)
            print("=====================================================")
    # image = page.viz()
    # plt.figure(figsize=(25, 17))
    # plt.axis('off')
    #
    # plt.imshow(image)
    # plt.show()


import PIL.PpmImagePlugin


def load_from_file_use_PIL(src_file: str) -> PIL.PngImagePlugin.PngImageFile:
    return Image.open(src_file, mode="r")
def load_from_file_as_numpy_array(src_file: str) -> numpy.ndarray:
    ret = cv2.imread(src_file)
    return ret


def show_numpy_array_as_image(data:numpy.ndarray,tile="ouput",width=1920,height=1080):
    # import plotly.express as px
    # fig = px.imshow(data)
    # fig.show()
    # cv2.imshow('image', data)
    # cv2.waitKey(0)
    cv2.namedWindow(tile, cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions
    cv2.resizeWindow(tile, width, height)

    cv2.imshow(tile, data)  # Show image
    cv2.waitKey(0)