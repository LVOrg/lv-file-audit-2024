from cyx.common import config
from cy_file_cryptor import wrappers
import cy_file_cryptor.context
from cyx import local_api_services
las = local_api_services.LocalAPIService()
token = las.get_access_token("admin/root","root")
cy_file_cryptor.context.set_server_cache(config.cache_server)
from cy_file_cryptor import security_context  as sc
from cy_file_cryptor.httpio import IORemote
# with sc.accquire(url="http://172.16.7.99/lvfile")
import requests
import requests
from io import BytesIO
from moviepy.editor import VideoFileClip
import imageio
import cv2
from cyx.common import config
url = "http://172.16.7.99/lvfile/api/lv-docs/file/f091c850-5ed4-4471-bd61-97ce9c60f6ae/whisng.mp4"
url2="http://172.16.7.99/lvfile/api/lv-docs/file/6906ea59-7f88-43e3-9486-ff752bd8089d/unknown_2023.03.13-19.05%20_1_.mp4"
url3=f"http://172.16.7.99/lvfile/api/lv-docs/file/f8f16850-163e-470b-af2a-a9f097c7d834/xx.mp4?token={token}"
fx = cv2.VideoCapture(url3)


num_frames_direct = int(fx.get(cv2.CAP_PROP_FRAME_COUNT))
fx.set(cv2.CAP_PROP_POS_FRAMES, num_frames_direct//2)
ret, frame = fx.read()

if not ret:
    print("Error reading frame.")
    fx.release()
    exit()
file_path=f'/mnt/files/__gemini_tmp__/long-test.png'
# Save the frame as a PNG file
# output_filename = f"frame_{frame_index}.png"
cv2.imwrite(file_path, frame)

mp4_file_path = f"/mnt/files/lv-docs/2024/03/14/mp4/f091c850-5ed4-4471-bd61-97ce9c60f6ae/whisng.mp4"
# with open(mp4_file_path,mode="rb") as fs:
#     video_reader = imageio.get_reader(fs)
#     frame = video_reader.get_data(12)
#     fx=1

response = requests.get(url, stream=True)
response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
with IORemote(url) as video_stream:

    video_reader = imageio.get_reader(video_stream)
    frame = video_reader.get_data(12)
    fx=1
# Open the response content as a byte stream
video_stream = BytesIO(response.content)

# Open the video stream using imageio
video_reader = imageio.get_reader(video_stream)

# Extract the desired frame
frame = video_reader.get_data(12)

# Cleanup: Close the video reader and response
video_reader.close()
response.close()


response = requests.get(url, stream=True)
response.raise_for_status()  # Raise an exception for 4XX or 5XX status codes
class CBytesIO(BytesIO):
    def __init__(self,url):
        self.url=url
from ffmpeg  import stream

# Open the response content as a byte stream
with IORemote(url) as video_stream:

    cv2.VideoCapture(video_stream)
    # Load the video clip using moviepy
    video_clip = VideoFileClip(video_stream)

    # Get a frame from the video (e.g., the first frame)
    frame = video_clip.get_frame(0)
    file_path=f'/mnt/files/__gemini_tmp__/long-test.png'
    imageio.imwrite(file_path, frame)
