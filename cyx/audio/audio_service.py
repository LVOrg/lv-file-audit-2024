import os.path
import typing
import uuid

import pydub
from pydub.silence import split_on_silence
class AudioService:
    def __init__(self):
        pass
    def silence_split(self,audio_file_path:str,output_dir:str)->typing.List[str]:

        output_dir_name = os.path.join(output_dir,str(uuid.uuid3()))
        if not os.path.isdir(output_dir_name):
            os.makedirs(output_dir_name,exist_ok=True)

        sound = pydub.AudioSegment.from_mp3(audio_file_path)

        min_silence_len = 500  # milliseconds
        silence_thresh = -40  # dBFS

        audio_chunks = split_on_silence(sound, min_silence_len, silence_thresh)
        ret =[]
        for chunk in audio_chunks:
            chunk.export(f"{output_dir_name}/output_{i}.mp3", format="mp3")
            ret+=[f"{output_dir_name}/output_{i}.mp3"]
        return ret