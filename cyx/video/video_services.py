import gc
import os.path
import pathlib
import pydub
import cv2
import numpy as np


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


class VideoInfo:
    fps: int
    duration: float
    width: int
    height: int

    def __repr__(self):
        return f"fps={self.fps},duration={self.duration},resolution={self.width}x{self.height}"


class VideoService:
    def __init__(self):
        pass

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
        # cap = cv2.VideoCapture(file_path)
        #
        # audio_data = np.empty(shape=(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 2), dtype=np.float32)
        # count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # for i in range(count):
        #     ret, frame = cap.read()
        #     if not ret:
        #         break
        #     audio_data[i] = frame[:, :, 1]
        #     printProgressBar(
        #         iteration=i,
        #         prefix="Process",
        #         length=50,
        #         total = count
        #     )
        #
        # cap.release()
        #
        # audio = pydub.AudioSegment.from_array(audio_data, format='float32')
        # audio.export(output_file, format='mp3')
        return output_file
