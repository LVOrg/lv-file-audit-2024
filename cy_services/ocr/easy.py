import typing
import numpy
import easyocr
from PIL.ImageFont import ImageFont
from PIL import Image, ImageFont, ImageDraw
from matplotlib import cm
import cy_kit
import matplotlib.pyplot as plt
from cy_services.datasets.manager import DatasetManagerService
from cy_services.spelling_corrector.english import SpellCorrectorService
from cy_services.base_services.base import BaseService
import cv2
from cy_vn_suggestion import suggest, correct_word
class BlockText:
    top_left:typing.Tuple[int,int]
    bottom_right: typing.Tuple[int, int]
    text:str
    correct_text: str
    index:int

class ReadTextService(BaseService):
    def __init__(
            self,
            dataset_manager= cy_kit.singleton(DatasetManagerService)
    ):
        print(self.config)
        self.dataset_manager = dataset_manager

        self.reader = easyocr.Reader(
            ["vi", "en"], gpu=False,
            model_storage_directory=self.dataset_manager.get_dataset_path("easyocr")
        )

    def read_with_block(self, img) -> typing.List[BlockText]:
        # https://analyticsindiamag.com/hands-on-tutorial-on-easyocr-for-scene-text-detection-in-images/
        # import matplotlib.pyplot as plt

        res = self.reader.readtext(img)
        rects = []
        index =0

        for (bbox, text, prob) in res:
            txt = correct_word(text)

            # unpack the bounding box
            (tl, tr, br, bl) = bbox
            tl = (int(tl[0]), int(tl[1]))
            # tr = (int(tr[0]), int(tr[1]))
            br = (int(br[0]), int(br[1]))
            # bl = (int(bl[0]), int(bl[1]))
            block_text = BlockText()
            block_text.top_left = tl
            block_text.bottom_right = br
            correct_text = txt
            block_text.text = text
            block_text.correct_text = correct_text
            block_text.index = index
            index += 1
            rects += [block_text]
        return rects

    def draw_result(self,data:typing.List[BlockText],img:numpy.ndarray)->numpy.ndarray:
        # import PIL

        # im = Image.fromarray(numpy.uint8(img))
        # draw = ImageDraw.Draw(im)
        # font = ImageFont.truetype("DejaVuSans.ttf", size=10)
        # font_color = (255, 0, 0)

        for x in data:
            cv2.rectangle(img, x.top_left, x.bottom_right, (0, 255, 0), 2)
            cv2.putText(img, x.index.__str__(), x.top_left,
                        cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
        # return numpy.asarray(im)
        return img



