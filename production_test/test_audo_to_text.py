#https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h
#https://huggingface.co/spaces/ntt123/vietTTS
import pathlib
import sys
import os
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
audio_file = f"/home/vmadmin/python/v6/file-service-02/audio-test/Một Đời Một Kiếp Quá Xa Xôi _1_.mp3"
audio_file_2 = f"/home/vmadmin/python/v6/file-service-02/audio-test/GiongDocTruyen.mp3"
from cyx.common.audio_utils import AudioService
audio_service = cy_kit.singleton(AudioService)
print(audio_service.get_duration(audio_file))
files = audio_service.split_by_seconds(audio_file_2,senconds=3)
import gradio
import cyx.document_layout_analysis.system
cyx.document_layout_analysis.system.set_offline_dataset(False)
from cyx.common.share_storage import ShareStorageService

share_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.abspath(
        os.path.join(share_storage_service.get_root(),"dataset")
    )
)
import torch
import torchaudio
from datasets import load_dataset
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
# test_dataset = load_dataset("common_voice", "vi", split="test")
# test_dataset = load_dataset("common_voice", "vi", split="test")
# split 'train', 'test', 'validation', 'other', 'validated', 'invalidated'
#test_dataset = load_dataset("common_voice", "vi", split="validated")
#mozilla-foundation/common_voice_11_0

test_dataset = load_dataset("mozilla-foundation/common_voice_11_0", "vi", split="train")
processor = Wav2Vec2Processor.from_pretrained("dragonSwing/wav2vec2-base-vietnamese")
model = Wav2Vec2ForCTC.from_pretrained("dragonSwing/wav2vec2-base-vietnamese")
model.gradient_checkpointing_enable()
resampler = torchaudio.transforms.Resample(48_000, 16_000)
# Preprocessing the datasets.
# We need to read the aduio files as arrays
audio_file = f"/home/vmadmin/python/v6/file-service-02/audio-test/510_cbsk___file_goc_510201920_3.wav"
audio_file_2 = f"/home/vmadmin/python/v6/file-service-02/audio-test/GiongDocTruyen.mp3"
audio_file_1 = f"/home/vmadmin/python/v6/file-service-02/audio-test/GiongMienNam.mp3"
def speech_file_to_array_fn(batch:dict):



    #data_waveform, rate_of_sample = torchaudio.load(audio_file)
    speech_array, sampling_rate = torchaudio.load(files[0])
    batch["speech"] = resampler(speech_array).squeeze().numpy()
    return batch
test_dataset = test_dataset.map(speech_file_to_array_fn)
inputs = processor(test_dataset["speech"][:2], sampling_rate=16_000, return_tensors="pt", padding=True)
with torch.no_grad():
  logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
predicted_ids = torch.argmax(logits, dim=-1)
print("Prediction:", processor.batch_decode(predicted_ids))
print("Reference:", test_dataset["sentence"][:2])
# test_dataset = test_dataset.map(speech_file_to_array_fn)
# print(type(test_dataset["speech"][:2][0]))
#inputs = processor(test_dataset["speech"][:2], sampling_rate=16_000, return_tensors="pt", padding=True)
# speech_array, sampling_rate = None, None
# # test_dataset = load_dataset("mozilla-foundation/common_voice_11_0", "vi", split="test")
# # test_dataset = test_dataset.map(speech_file_to_array_fn)
# try:
#
#     # torchaudio.datasets.commonvoice.Dataset = load_dataset("common_voice", "vi", split="test")
#     speech_array, sampling_rate = torchaudio.load(audio_file)
#     print(len(speech_array))
# except Exception as  e:
#     print(e)
# inputs = processor(speech_array[0], sampling_rate=16_000, return_tensors="pt", padding=True)
# with torch.no_grad():
#   logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
# predicted_ids = torch.argmax(logits, dim=-1)
# print("Prediction:", processor.batch_decode(predicted_ids))

