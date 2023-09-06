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

    def extract_text(self,file_name:str)->dict:
        reader = easyocr.Reader(['en', 'vi'])
        # Open the video file
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
        while True:
            # Read the next frame
            ret, frame = cap.read(frame_index)

            # If the frame is not read successfully, break
            if not ret:
                break

            # Detect and recognize text in the frame
            texts = reader.readtext(frame, detail=0)
            text = " ".join(texts)
            self.console.progress_bar(
                iteration= frame_index,
                total = frames_count,
                prefix="Read text"
            )

            # Check if the text is a caption

            if len(text) > 10:
                # Detect the language of the text
                language = langdetect.detect(text)

                # Check if the language is in the list of languages
                if language not in ["en", "vi"]:
                    continue

            # Calculate the time in seconds
            time_in_seconds = start_time + (fps * frame_index)
            frame_index += fps * 5

            # Add the caption to the list of captions
            captions.append(text)

            # Add the time of the caption to the list of times
            times.append(time_in_seconds)

        # Close the video file
        cap.release()

        # Print the captions and their times
        ret = dict(zip(captions, times))
        return ret