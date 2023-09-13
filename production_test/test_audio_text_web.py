import pathlib
import sys
import os
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.share_storage import ShareStorageService
import cyx.document_layout_analysis.system
share_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_offline_dataset(True)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.join(share_storage_service.get_root(),"dataset")
)



import gradio
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




def transcribe(audio):
    global test_dataset

    sample_rate, waveform = audio
    # if len(waveform.shape) == 2:
    #     waveform = waveform[:, 0]
    # waveform = torch.from_numpy(waveform).float().unsqueeze_(0)
    # # waveform = torchaudio.functional.resample(waveform, sample_rate, 16_000)
    # waveform = resampler(waveform).squeeze().numpy()
    # def speech_file_to_array_fn(batch: dict):
    #     # data_waveform, rate_of_sample = torchaudio.load(audio_file)
    #     # speech_array, sampling_rate = torchaudio.load(audio)
    #     # batch["speech"] = resampler(audio).squeeze().numpy()
    #     batch["speech"] = waveform
    #     return batch
    #
    # test_dataset = test_dataset.map(speech_file_to_array_fn)
    # inputs = processor(test_dataset["speech"][:2], sampling_rate=16_000, return_tensors="pt", padding=True)
    # waveform = resampler(waveform).squeeze().numpy()
    # data_wave = resampler(waveform).squeeze().numpy()
    # inputs = processor(data_wave[:2], sampling_rate=16_000, return_tensors="pt", padding=True)
    inputs = processor(waveform[:2], sampling_rate=16_000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcript = processor.batch_decode(predicted_ids)
    # print("Prediction:", transcript)
    # print("Reference:", test_dataset["sentence"][:2])
    # sample_rate, waveform = audio
    # if len(waveform.shape) == 2:
    #     waveform = waveform[:, 0]
    # waveform = torch.from_numpy(waveform).float().unsqueeze_(0)
    # waveform = torchaudio.functional.resample(waveform, sample_rate, 16_000)
    #
    # transcript = model.predict(waveform)[0]
    #
        return transcript

# gradio.Interface(fn=transcribe, inputs=gradio.Audio(source="microphone", type="numpy"), outputs="textbox").launch(
#     server_name="0.0.0.0",
#     server_port=8013
#
# )
gradio.Interface(fn=transcribe, inputs=gradio.Audio(type="numpy"), outputs="textbox").launch(
    server_name="0.0.0.0",
    server_port=8013

)