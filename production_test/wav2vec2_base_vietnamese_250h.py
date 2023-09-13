#https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.share_storage import ShareStorageService
import cyx.document_layout_analysis.system
import os
share_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_offline_dataset(False)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.join(share_storage_service.get_root(),"dataset")
)
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch

# load model and tokenizer
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch

# load model and tokenizer
fx ="dragonSwing/wav2vec2-base-vietnamese"
fy= "nguyenvulebinh/wav2vec2-base-vietnamese-250h"
fz= "mozilla-foundation/common_voice_11_0"
f=fx
processor = Wav2Vec2Processor.from_pretrained(f)
model = Wav2Vec2ForCTC.from_pretrained(f)

# define function to read in sound file
def map_to_array(batch):
    speech, _ = sf.read(batch["file"])
    batch["speech"] = speech
    return batch

# load dummy dataset and read soundfiles
file ="/home/vmadmin/python/v6/file-service-02/audio-test/chunk0.mp3"
ds = map_to_array({
    "file": file
})

# tokenize
input_values = processor(ds["speech"], return_tensors="pt", padding="longest").input_values  # Batch size 1

# retrieve logits
logits = model(input_values).logits

# take argmax and decode
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)
print(transcription)