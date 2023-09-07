import gc
import os.path
import pathlib
import pydub
import cv2
import numpy as np
import cv2
import easyocr
import time
import langdetect
from fuzzywuzzy import fuzz
import pytesseract
import PIL


class VideoInfo:
    fps: int
    duration: float
    width: int
    height: int

    def __repr__(self):
        return f"fps={self.fps},duration={self.duration},resolution={self.width}x{self.height}"

from cyx.common.temp_file import TempFiles
from cyx.console.console_services import ConsoleServices
import cy_kit
class VideoService:
    def __init__(self,
                 tmp_file = cy_kit.singleton(TempFiles),
                 console = cy_kit.singleton(ConsoleServices)
                 ):
        self.tmp_file = tmp_file
        self.console = console

    def get_info(self, file_path: str) -> VideoInfo:
        cap = cv2.VideoCapture(file_path)
        ret = VideoInfo()
        ret.fps = cap.get(cv2.CAP_PROP_FPS)
        ret.duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / ret.fps
        ret.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        ret.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        del cap
        gc.collect()
        return ret

    def extract_audio(self, file_path: str, output_dir: str) -> str:
        file_name = pathlib.Path(file_path).name
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{file_name}.mp3")
        import moviepy.editor as mp
        clip = mp.VideoFileClip(file_path)
        clip.audio.write_audiofile(output_file)

        return output_file

    def extract_text(self,file_name:str,langs =["vi","en"],elapse_time_in_seconds =5)->dict:
        reader = easyocr.Reader(langs)
        # Open the video file
        info =self.get_info(file_name)
        cap = cv2.VideoCapture(file_name)
        frames_count =  cap.get(cv2.CAP_PROP_FRAME_COUNT)
        # Set the start time to zero
        start_time = 0

        # Get the FPS
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Initialize a list to store the captions
        captions = []

        # Initialize a list to store the times of the captions
        times = []

        # Loop over the frames in the video
        frame_index = 0
        is_continue  =  (frame_index< frames_count)
        old_text = ""
        while is_continue:
            # Read the next frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

            ret, frame = cap.read(frame_index)

            # If the frame is not read successfully, break
            if not ret:
                break


            # Detect and recognize text in the frame

            texts = reader.readtext(frame, detail=0)
            # text = pytesseract.image_to_string(frame,lang="eng+vie")


            del frame
            gc.collect()
            text = " ".join(texts)
            ratio = fuzz.ratio(old_text, text)
            if ratio < 25.0:
                captions.append(text)
                times.append(time_in_seconds)
            time_in_seconds = start_time + (fps * frame_index)
            old_text = text

            self.console.progress_bar(
                iteration=frame_index,
                total=frames_count,
                prefix="Read text",
                printEnd=f"Found {len(captions)},info={info},{frame_index}/{frames_count}",
                length=50
            )
            frame_index = min(frames_count,frame_index+fps * elapse_time_in_seconds)
            is_continue = (frame_index < frames_count)
            if frame_index>frames_count:
                break

        # Close the video file
        cap.release()
        print("Finish, collecting data ...")

        # Print the captions and their times
        ret = dict(zip(captions, times))
        return ret