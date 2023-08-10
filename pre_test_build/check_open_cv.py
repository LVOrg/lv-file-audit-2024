import os.path
import pathlib
_wrking_dir_ = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(_wrking_dir_)
# import pika
# raise Exception(pika.__file__)
import cv2

# if os.path.isdir(pathlib.Path(cv2.__file__).parent.__str__()):
#     raise Exception(pathlib.Path(cv2.__file__).parent.__str__())
file_test = os.path.join(pathlib.Path(__file__).parent.__str__(),"test.png")
file_output = os.path.join(pathlib.Path(__file__).parent.__str__(),"test1.png")
im_gray = cv2.imread(file_test, cv2.IMREAD_GRAYSCALE)
(thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 127
im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
cv2.imwrite(file_output, im_bw)