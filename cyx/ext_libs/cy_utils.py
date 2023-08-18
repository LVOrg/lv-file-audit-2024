import logging
import os
import pathlib
import typing
import pytesseract
import ocrmypdf
import PyPDF2
import img2pdf
import langdetect
import underthesea
from easyocr import easyocr
import numpy as np
import cv2
from cyx.ext_libs.vn_predicts import predict_accents, get_config
from PIL import Image

__working_dir__ = pathlib.Path(__file__).parent.parent.parent.__str__()
__log_dir__ = None
__log_dir_path__ = None
__logger__ = None
__easy_ocr_to_tesseract_langs_map__ = {
    'af': 'af',
     'am': 'am',
     'ar': 'ara',
     'az': 'az',
     'be': 'be',
     'bg': 'bg',
     'bn': 'bn',
     'bs': 'bs',
     'ca': 'cat',
     'ceb': 'ceb',
     'chinese': 'chi_sim',
     'cs': 'cs',
     'da': 'dan',
     'de': 'deu',
     'el': 'ell',
     'es': 'spa',
     'et': 'est',
     'fa': 'fas',
     'fi': 'fin',
     'fr': 'fra',
     'gu': 'gug',
     'hi': 'hin',
     'hr': 'hrv',
     'hu': 'hun',
     'id': 'ind',
     'it': 'ita',
     'ja': 'jpn',
     'ka': 'kat',
     'ko': 'kor',
     'lt': 'lit',
     'lv': 'lav',
     'mk': 'mkd',
     'mn': 'mon',
     'nl': 'nld',
     'no': 'nor',
     'pl': 'pol',
     'pt': 'por',
     'ro': 'ron',
     'ru': 'rus',
     'sk': 'slk',
     'sl': 'slv',
     'sr': 'srp',
     'sv': 'swe',
     'ta': 'tam',
     'th': 'tha',
     'tl': 'tgl',
     'tr': 'tur',
     'uk': 'ukr',
     'ur': 'urd',
     'vi': 'vie',
     'zh': 'zh_sim',
     'zh_tra':'zh_tw'
}
__tesseract_to_easy_ocr_langs_map__  = dict([(v,k) for k,v in __easy_ocr_to_tesseract_langs_map__.items()])
class Files:
    """
    All utilities of file such as: path maker, converter
    """

    @staticmethod
    def convert_file_ext(file_path: str, ext: str):
        """
        Make a new path from file_path by replacing ext of file
        :param file_path:
        :param ext:
        :return:
        """
        dir_to_ext = pathlib.Path(file_path).parent.__str__()
        file_name = pathlib.Path(file_path).stem
        ret = os.path.abspath(
            os.path.join(dir_to_ext, file_name + "." + ext)
        )
        return ret

class Images:
    @staticmethod
    def poly_lines(image:str,polylines_list:typing.List[typing.List[typing.Tuple[int,int]]]):
        image = cv2.imread(image)
        # Get the coordinates of the polygon.
        points = [np.array(x,np.int32) for x in polylines_list]
        cv2.polylines(image, points, True, (0, 255, 0), thickness=2)

        return image
        # Draw the polygon.

class Tesseract:
    @staticmethod
    def get_langs_support():
        languages = pytesseract.get_languages()
        return languages

    @staticmethod
    def get_boxes(img, lang=None):
        if not lang:
            lang = Tesseract.get_langs_support()
        __lang__ = "+".join(lang)
        ret = pytesseract.image_to_boxes(img, __lang__, output_type="dict")
        return ret

    @staticmethod
    def get_text(img, lang=None):
        if not lang:
            lang = Tesseract.get_langs_support()
        __lang__ = "+".join(lang)
        ret = pytesseract.image_to_string(img, __lang__)
        return ret

class EasyOCR:
    @staticmethod
    def get_text(img,langs:typing.List[str]=["ch","vi","ko"]):
        __langs_ =[x for x in langs if __easy_ocr_to_tesseract_langs_map__.get(x) is not None]
        reader = easyocr.Reader(__langs_)
        ret = reader.readtext(img,detail=0)
        return ret

    @staticmethod
    def get_data(img, langs: typing.List[str] = ["ch", "vi", "ko"]):
        __langs_ = [x for x in langs if __easy_ocr_to_tesseract_langs_map__.get(x) is not None]
        reader = easyocr.Reader(__langs_)
        ret = reader.readtext(img)
        lst = []
        np_polylines=[]
        for x, y, z in ret:
            e = dict(
                coords=[dict(x=int(v[0]), y=int(v[1])) for v in x],
                points=[(int(v[0]),int(v[1])) for v in x],
                text=y,
                score=z
            )
            lst += [e]
            np_polylines += [x]
        return lst,ret,np_polylines
class OCR:
    @staticmethod
    def from_pdf(pdf_file: str, lans: typing.Optional[typing.List[str]] = None):
        __langs__ = lans or Tesseract.get_langs_support()
        pdf_output = Files.convert_file_ext(pdf_file, ".orc.pdf")
        ocrmypdf.ocr(
            input_file=pdf_file,
            output_file=pdf_output,
            progress_bar=False,
            language="+".join(__langs__),
            use_threads=False,
            skip_text=False,
            force_ocr=True,
            deskew=True,
            jobs=50,
            # optimize=3,
            keep_temporary_files=False
        )
        return pdf_output


class ContentReader:
    @staticmethod
    def read_text_from_pdf(pdf_file_path):
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text


class Converter:
    @staticmethod
    def image_to_pdf(image_path: str, pdf_path: str):
        pdf = img2pdf.convert(image_path)
        with open(pdf_path, "wb") as f:
            f.write(pdf)


class Linguistics:
    @staticmethod
    def detect_langs(text: str):
        try:
            return langdetect.detect(text)
        except:
            return None

    @staticmethod
    def segment_word(text: str):
        return underthesea.word_tokenize(text)

    @staticmethod
    def vn_suggest_from_none_accents(text: str):
        get_config()
        return predict_accents(text)

class Loggers:
    @staticmethod
    def get_directory() -> str:
        global __log_dir__
        global __working_dir__
        if __log_dir__ is None:
            __log_dir__ = os.path.abspath(
                os.path.join(__working_dir__, "share-storage", "logger")
            )
        if not os.path.isdir(__log_dir__):
            os.makedirs(__log_dir__, exist_ok=True)
        return __log_dir__

    @staticmethod
    def get_path() -> str:
        global __log_dir_path__
        if __log_dir_path__ is None:
            __log_dir_path__ = os.path.join(Loggers.get_directory(), "logs.log")
        return __log_dir_path__

    @staticmethod
    def __get_logger__() -> logging.Logger:
        global __logger__
        if __logger__ is None:
            __logger__ = logging.getLogger("centralize")

            # Set the logging level to DEBUG
            __logger__.setLevel(logging.DEBUG)

            # Create a file handler and set the file path
            file_handler = logging.FileHandler(Loggers.get_path())

            # Set the format for the log messages
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            # Add the file handler to the logger
            __logger__.addHandler(file_handler)
        return __logger__

    @staticmethod
    def info(msg):
        Loggers.__get_logger__().info(msg, exc_info=True)

    @staticmethod
    def error(ex):
        Loggers.__get_logger__().exception("An exception occurred: %s", ex, exc_info=True)
