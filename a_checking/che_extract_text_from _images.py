import cy_kit
from cyx.easy_ocr import EasyOCRService
es=cy_kit.singleton(EasyOCRService)
fx=es.get_text("/home/vmadmin/python/cy-py/a_checking/resources/26760_ram_kingston_laptop_1_1.jpg")
print(fx)
import cv2

# Replace 'your_video.mp4' with the path to your video file
video_path = "http://172.16.7.99/lvfile/api/developer/file/63e2a5a6-85cf-49a3-a3e5-bb8e81e1a46e/pexels-cottonbro-5532772%20_240p_.mp4"

cap = cv2.VideoCapture(video_path)

# Check if video was opened successfully
if not cap.isOpened():
  print("Error opening video file")
  exit()

# Get the total number of frames using cv2.CAP_PROP_FRAME_COUNT
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

# Print the total number of frames
print("Total frames in video:", int(total_frames))

# Release the video capture object
cap.release()
file = "http://172.16.7.99/lvfile/api/developer/file/63e2a5a6-85cf-49a3-a3e5-bb8e81e1a46e/pexels-cottonbro-5532772%20_240p_.mp4"