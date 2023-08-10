import cv2
import numpy
def show_image(data: numpy.ndarray, tile="ouput", width=1920, height=1080):
    """
    Shaw image and wait until key hit by developer
    :param data:
    :param tile:
    :param width:
    :param height:
    :return:
    """
    cv2.namedWindow(tile, cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions
    cv2.resizeWindow(tile, width, height)

    cv2.imshow(tile, data)  # Show image
    cv2.waitKey(0)
