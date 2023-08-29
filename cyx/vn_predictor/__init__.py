import pathlib
import os
from cy_vn import predict_accents,get_config
from cy_vn_suggestion import suggest
__working_path__ = pathlib.Path(__file__).parent.parent.parent.__str__()
class VnPredictor:
    def __init__(self):

        self.working_path = __working_path__
        # self.data_set_dir = os.path.join(self.working_path, "share-storage", "cy_vn")
        # get_config(self.data_set_dir)
    def get_text(self,content:str)->str:
        return suggest(content)
        # return predict_accents(content)


