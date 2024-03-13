from cyx.common  import config
from cy_file_cryptor import wrappers
from moviepy.editor import *
import cv2

file_path="http://172.16.7.99/lvfile/api/lv-docs/file/215682b9-9771-44f9-a607-1d5af12e503a/xx.mp4"
#D:\codx-file-storage\files\lv-docs\2024\03\13\mp4\1c387233-9bf8-4a0d-939d-bbcec7bf36c6
file_test = os.path.join(config.file_storage_path,"lv-docs/2024/03/13/mp4/1c387233-9bf8-4a0d-939d-bbcec7bf36c6/bandicam 2023-08-11 11-51-55-581.mp4")
# clip = VideoFileClip(
#             file_test
#         )
# fx= clip
cap = cv2.VideoCapture(file_path)
print(cap)