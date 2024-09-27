"""
THis package use Paddle OCR for layout analyzer the use VieOCR for Vietnamese Text
"""
import hashlib
import os
import sys

import pathlib

sys.path.append("/app")
torch_path = os.path.join(pathlib.Path(__file__).parent.parent.__str__(), "py-torch")
torch_path_cache = os.path.join(pathlib.Path(__file__).parent.parent.__str__(), "py-torch", "cache")
os.makedirs(torch_path_cache, exist_ok=True)
""""
ENV_TORCH_HOME = 'TORCH_HOME'
ENV_XDG_CACHE_HOME = 'XDG_CACHE_HOME'
"""
os.environ['TORCH_HOME'] = torch_path
os.environ['XDG_CACHE_HOME'] = torch_path_cache
import paddleocr

paddleocr.paddleocr.BASE_DIR = os.path.join(torch_path, "paddleocr")
os.makedirs(paddleocr.paddleocr.BASE_DIR, exist_ok=True)
from paddleocr import PaddleOCR
from cy_lib_ocr.pdf_services import PDF_Service
import typing
import cy_kit
import matplotlib.pyplot as plt
from PIL import Image

from icecream import ic

# import torch.hub
# print(torch.hub._get_torch_home())
#
# torch.hub.DEFAULT_CACHE_DIR =torch_path_cache
#
# os.environ[torch.hub.ENV_TORCH_HOME]= torch_path
# # model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True, download_dir=r'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking')
# print(os.environ[torch.hub.ENV_TORCH_HOME])
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from cyx.common import config
import requests
from retry import retry
from tika import parser as tika_parse

import yaml
class OCRService:
    pdf_service = cy_kit.singleton(PDF_Service)

    def __init__(self):
        self.module_dir = pathlib.Path(__file__).parent.__str__()
        base_config_path = os.path.join(self.module_dir,"config","base.yml")
        base_config_vgg_transformer = os.path.join(self.module_dir, "config", "vgg_transformer.yml")
        self.base_config={}
        with open(base_config_path, "r") as file:
            self.base_config = yaml.safe_load(file)

        # self.config = Cfg.load_config_from_name('vgg_transformer')
        self.config = {
            "weights": os.path.join(torch_path, "vgg_transformer.pth"),
            "backbone": "vgg19_bn",
            "cnn": {
                "pretrained": False,
                "ss":[[2, 2],[2, 2],[2, 1],[2, 1],[1, 1]],
                # pooling kernel size
                "ks":[[2, 2],[2, 2],[2, 1],[2, 1],[1, 1]],
                # dim of ouput feature map
                "hidden": 256
            }

        }
        for k,v in self.base_config.items():
            self.config[k] = v
        self.config['weights'] = os.path.join(torch_path, "vgg_transformer.pth")
        self.config['cnn']['pretrained'] = False
        self.config['device'] = 'cpu'
        ic(self.config)
        self.detector = Predictor(self.config)
        self.tmp_output_dir = os.path.join(config.file_storage_path, "__tmp_viet_ocr__")
        self.tmp_result_dir = os.path.join(config.file_storage_path, "__tmp_viet_ocr_result__")
        os.makedirs(self.tmp_output_dir, exist_ok=True)
        os.makedirs(self.tmp_result_dir, exist_ok=True)

    def check(self):
        ic(self.config)
    def extract_text_by_using_tika_server(self, file_path: str):
        @retry(exceptions=(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError), delay=15, tries=10)
        def runing():
            parsed_data = tika_parse.from_file(file_path,
                                               serverEndpoint=config.tika_server,
                                               xmlContent=False,
                                               requestOptions={'timeout': 5000})

            content = parsed_data.get("content", "") or ""
            content = content.lstrip('\n').rstrip('\n').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            while "  " in content:
                content = content.replace("  ", " ")
            content = content.rstrip(' ').lstrip(' ')
            return content

        return runing()

    def do_detector(self, image_path: str):

        img = Image.open(image_path)

        s = self.detector.predict(img)
        return s

    def extract_subimage(self, image, x1, y1, x2, y2):
        """
        Extracts a subimage from a PIL Image based on given coordinates.

        Args:
          image: The original PIL Image.
          x1, y1: The top-left coordinates of the subimage.
          x2, y2: The bottom-right coordinates of the subimage.

        Returns:
          A new PIL Image containing the extracted subimage.
        """

        width = x2 - x1
        height = y2 - y1
        return image.crop((x1, y1, x1 + width, y1 + height))

    def do_detect_image(self, img: Image):
        s = self.detector.predict(img)
        return s

    def get_text_rect_from_image(self, image_path: str, lang="en") -> typing.Iterable[
        typing.Tuple[float, float, float, float]]:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang)  # need to run only once to download and load model into memory
        img = Image.open(image_path)
        result = ocr.ocr(image_path, cls=True)
        for line in result:
            for x in line:
                x1, y1, x2, y2 = self.find_coordinates(x[0])
                sub_img = self.extract_subimage(img, x1, y1, x2, y2)
                txt = self.detector.predict(sub_img)
                yield txt

    def find_coordinates(self, points):
        """
        Finds the coordinates of the top-left and bottom-right corners of a rectangle
        defined by a list of points.

        Args:
          points: A list of points in the format [x, y].

        Returns:
          A tuple of coordinates (x1, y1, x2, y2) representing the top-left and bottom-right
          corners of the rectangle.
        """

        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        return (min_x, min_y, max_x, max_y)

    def get_text_from_pdf(self, pdf_file) -> typing.Union[str, None]:
        tika_content = self.extract_text_by_using_tika_server(pdf_file) or ""
        try:
            file_iter: typing.Iterable[str] = self.pdf_service.image_extract(pdf_file_path=pdf_file,
                                                                             output_dir=self.tmp_output_dir)
            contents = []
            for x in file_iter:
                for rect in self.get_text_rect_from_image(x):
                    ic(rect)
                    contents.append(rect)
            contents.append(tika_content)
            return " ".join(contents)
        except RuntimeError:
            return tika_content


    def get_content_from_pdf(self, pdf_file):
        """
        Do OCR and write content to file return that file
        @param pdf_file:
        @return:
        """
        # first has256 location of pdf file as content file name
        content_file_name = hashlib.sha256(pdf_file.encode()).hexdigest()
        content_file_path = os.path.join(self.tmp_result_dir, f"{content_file_name}.txt")
        # check if content_file_path is ready that mean pdf_file has been OCR-Content, no more do OCR
        if os.path.isfile(content_file_path):
            return content_file_path
        # do OCR content
        content = self.get_text_from_pdf(pdf_file)
        content = content.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        while "  " in content:
            content = content.replace("  ", " ")
        content = content.lstrip(" ").rstrip(" ")
        with open(content_file_path, "wb") as fs:
            fs.write(content.encode())
        return content_file_path




def main():
    svc = OCRService()
    pdf_file = r'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/511-cp.signe.pdf'
    pdf_file = r'/app/a_checking/resource-test/511-cp.signe.pdf'
    pdf_file = r'/app/a_checking/resource-test/qð 542.pdf'
    pdf_file = r'/app/a_checking/resource-test/2024-3dn-puq00044_cong van.pdf'
    output_dir = f'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/results'
    output_dir = f'/app/a_checking/resource-test/results-docker'
    # file_iter: typing.Iterable[str] = svc.pdf_service.image_extract(pdf_file_path=pdf_file, output_dir=output_dir)
    # for x in file_iter:
    #     for rect in svc.get_text_rect_from_image(x):
    #         print(rect)
    # txt_content: typing.Union[str,None] = svc.get_text_from_pdf(pdf_file)
    txt_content = svc.get_content_from_pdf(pdf_file)
    ic(txt_content)


if __name__ == "__main__":
    main()
