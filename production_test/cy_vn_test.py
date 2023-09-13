import pathlib
working_dir = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(working_dir)
import cy_kit
from cyx.vn_predictor import VnPredictor
svc= cy_kit.singleton(VnPredictor)
txt = svc.get_text("Thu cai coi")
print(txt)
