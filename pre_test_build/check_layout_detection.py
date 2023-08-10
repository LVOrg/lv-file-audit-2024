import os
if not os.path.isfile("/usr/bin/tesseract"):
    raise Exception(f"'/usr/bin/tesseract' was not found")
import doctr
if doctr.__version__!="v0.6.0":
    raise Exception(f"doctr version require is v0.6.0. But found {doctr.__version__}")
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.datasets import CORD
import deepdoctection
if str(deepdoctection.__version__)!="0.21":
    raise Exception(f"deepdoctection version require is 0.211. But found {deepdoctection.__version__}")
from deepdoctection.dataflow.serialize import DataFromList


import datasets
if datasets.__version__!="2.10.2.dev0":
    raise Exception(f"datasets version require is 2.10.2.dev0. But found {datasets.__version__}")
import transformers
if transformers.__version__!="4.28.0.dev0":
    raise Exception(f"transformers version require is 4.28.0.dev0. But found {transformers.__version__}")
import detectron2
if detectron2.__version__!="0.4":
    raise Exception(f"detectron2 version require is 0.4. But found {detectron2.__version__}")
import packaging
if packaging.__version__!="21.3":
    raise Exception(f"packaging version require 21.3. But found {packaging.__version__}")