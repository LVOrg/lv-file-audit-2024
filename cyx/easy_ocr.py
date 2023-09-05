"""
Use easyocr to OCR an image \n
EasyOCRService is Class
"""
import os.path
import pathlib
import typing

import easyocr
import cy_kit
from cyx.vn_predictor import VnPredictor
from cyx.common.temp_file import TempFiles
from cyx.common.share_storage import ShareStorageService
__model_storage_directory__ = os.path.abspath(
    os.path.join(
        pathlib.Path(__file__).parent.parent.__str__(),
        "dataset",
        "easyocr"
    )

)
"""
easyocr use dataset to recognize text. This variable is the location of dataset dir 
"""

class DouTextInfo:
    content: typing.List[str]

    suggest_content: str

from cyx.utils import easyocr_get_langs_suport
class EasyOCRService:
    """
    This is a service use: \n
    cyx.vn_predictor.VnPredictor and cyx.common.TempFiles \n
    cyx.vn_predictor.VnPredictor was written in C# and compiler by dot net core 5.0 \n
    cyx.common.TempFiles is a manager of temp-file-processing \n

    Đây là cách sử dụng dịch vụ: \n
    cyx.vn_predictor.VnPredictor và cyx.common.TempFiles \n
    cyx.vn_predictor.VnPredictor được viết bằng C# và trình biên dịch bởi dot net core 5.0 \n
    cyx.common.TempFiles là trình quản lý xử lý tệp tạm thời \n
    """
    def __init__(
            self,
            vn_predict=cy_kit.singleton(VnPredictor),
            tmp_file=cy_kit.singleton(TempFiles),
            share_storage=cy_kit.singleton(ShareStorageService)
    ):
        self.share_storage=share_storage
        self.__data_set_path__ = os.path.abspath(
            os.path.join(self.share_storage.get_root(),"dataset","easyocr")
        )
        print(f"EasyOCR will locate dataset at ")
        self.use_gpu = False
        self.langs = ["vi","en"]
        self.reader = easyocr.Reader(
            self.langs, gpu=self.use_gpu,
            model_storage_directory=self.__data_set_path__
        )
        self.vn_predict = vn_predict
        self.tmp_file = tmp_file

    def get_duo_text(self, image_file: str) -> dict:
        ret = {}
        if os.path.isfile(image_file):
            lst_text = self.reader.readtext(image_file, detail=0)

            for x in lst_text:
                ret[x] = self.vn_predict.get_text(x)

            # ret_1 = "\n".join(results)
            # _r =[]
            # for x in results:
            #     _r+=[self.vn_predict.get_text(x)]
            #
            # ret = " ".join(_r)
            # return ret+"\n"+ret_1
            return ret

    def get_text(self, image_file: str) -> str:
        if os.path.isfile(image_file):
            results = self.reader.readtext(image_file, detail=0)
            ret_1 = "\n".join(results)
            _r = []
            for x in results:
                _r += [self.vn_predict.get_text(x)]

            ret = " ".join(_r)
            return ret + "\n" + ret_1
        else:
            return  ""
