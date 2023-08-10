import uuid

from pydub import AudioSegment
import math
import cy_kit
from cyx.common.share_storage import ShareStorageService
import os
import librosa
import soundfile
from pydub import AudioSegment
from pydub.silence import split_on_silence

class AudioService:
    def __init__(self, share_storage_service: ShareStorageService = cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service
        self.processing_folder = self.share_storage_service.get_temp_dir(AudioService)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def get_duration(self, audio_file: str):

        f = soundfile.SoundFile(audio_file)
        print('samples = {}'.format(f.frames))
        print('sample rate = {}'.format(f.samplerate))
        print('seconds = {}'.format(f.frames / f.samplerate))

        return f

    def split_by_seconds(self, audio_file: str, senconds: int = 30):
        ret = []
        output_dir = os.path.abspath(
            os.path.join(self.processing_folder, str(uuid.uuid4()))
        )
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        x, sr = librosa.load(audio_file, sr=None)
        for i in range(0, len(x), senconds * sr):
            y = x[senconds * sr * i: senconds * sr * (i + 1)]
            output_file = os.path.join(output_dir, "chunk{0}.mp3".format(i))
            print(output_file)
            soundfile.write(output_file, y, sr)
            ret += [output_file]
        return ret

    def split(self, audio_file: str):
        ret = []

        # reading from audio mp3 file
        print("load audio file")
        print(audio_file)
        sound = AudioSegment.from_mp3(audio_file)
        output_dir = os.path.abspath(
            os.path.join(self.processing_folder, str(uuid.uuid4()))
        )
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        # spliting audio files
        print("split audio file according to silence ")
        audio_chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=-40)
        # loop is used to iterate over the output list
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join(output_dir, "chunk{0}.mp3".format(i))
            print("Exporting file", output_file)
            chunk.export(output_file, format="mp3")
            ret += [output_file]
        return ret
