import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import torch
import torchaudio
from datasets import load_dataset
import datasets
import transformers
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import cyx.common.audio_utils
from cyx.common.audio_utils import AudioService
print(f"torch.__version__={torch.__version__}")
print(f"torchaudio.__version__={torchaudio.__version__}")
print(f"datasets.__version__={datasets.__version__}")
print(f"transformers.__version__={transformers.__version__}")
