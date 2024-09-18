import os
import huggingface_hub.file_download

huggingface_hub.file_download.HUGGINGFACE_HUB_CACHE = f"/home/vmadmin/python/v6/file-service-02/dataset"

print(huggingface_hub.file_download.HUGGINGFACE_HUB_CACHE)
os.environ['CURL_CA_BUNDLE'] = ''
import pathlib
import shutil
import cyx.document_layout_analysis.system

working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
lib_path = pathlib.Path(__file__).parent.parent.__str__()
import os

# os.environ["XDG_CACHE_HOME"] = cyx.document_layout_analysis.system.set_dataset_path()
# os.environ["DOCTR_CACHE_DIR"] = f"{working_dir}/dataset/doctr"

# os.environ["DOCTR_CACHE_DIR"]= f"{working_dir}/dataset"
from doctr.io import DocumentFile

from doctr.models import ocr_predictor
from doctr.datasets import CORD

deepdoctection_analyzer = None

import deepdoctection


class DoctrService:
    """
    This service will install DocTr service with Tesseract.
    Service also detect if thou's OS has Tesseract.
    If thou's OS does not have Tesseract it will cause an error
    In the case,  Tesseract is already in thou's OS, the service will detect all language and install DocTr
    If the service did not find any language of Tesseract in thou's OS it will use English as default
    ------------------- \n
    Dịch vụ này sẽ cài đặt dịch vụ DocTr với Tesseract.
    Dịch vụ cũng phát hiện xem hệ điều hành của bạn có Tesseract hay không.
    Nếu hệ điều hành của bạn không có Tesseract, nó sẽ gây ra lỗi
    Trong trường hợp Tesseract đã có trong hệ điều hành của bạn, dịch vụ sẽ phát hiện tất cả ngôn ngữ và cài đặt DocTr
    Nếu dịch vụ không tìm thấy bất kỳ ngôn ngữ nào của Tesseract trong hệ điều hành của bạn, dịch vụ sẽ sử dụng tiếng Anh làm mặc định
    """

    def __init__(self):
        self.__lan__ = "+".join(cyx.document_layout_analysis.system.get_languages())
        self.__has_init__ = False
        self.__analyzer__ = None

    def get_analyzer(self) -> deepdoctection.DoctectionPipe:
        """
        Install Tesseract with installed-language into DocTr
        This is really importance thing to force Doctr use Tesseract and installed-language to layout detection
        ----------------------- \n
        Cài đặt Tesseract với ngôn ngữ cài đặt vào DocTr
        Đây thực sự là điều quan trọng để buộc Doctr sử dụng Tesseract và ngôn ngữ cài đặt để phát hiện bố cục
        :return:
        """
        if self.__analyzer__ is None:
            if not deepdoctection.tesseract_available():
                raise Exception("tesseract is not available")

            self.__analyzer__ = deepdoctection.get_dd_analyzer(
                language=self.__lan__

            )

        return self.__analyzer__

    def __build__(self):
        """
        Use when debug or developer mode not for Production
        :return:
        """
        if self.__has_init__:
            return self
        self.__has_init__ = True
        global working_dir
        global lib_path

        self.dataset_model_path = os.path.abspath(
            os.path.join(lib_path, "dataset-model", "model_final_inf_only.pt")
        )

        self.dataset_dir = cyx.document_layout_analysis.system.get_dataset_path()
        # os.path.join(working_dir, "dataset")
        self.deepdoctection_weights_layout_finale_model_dir = os.path.abspath(
            os.path.join(
                self.dataset_dir,
                "deepdoctection",
                "weights",
                "layout"
            )
        )

        self.model = ocr_predictor(
            pretrained=True,
            detect_language=False,
            export_as_straight_boxes=True,
            detect_orientation=True
        )
        import deepdoctection as dd

        global deepdoctection_analyzer
        if deepdoctection_analyzer is None:

            if not dd.tesseract_available():
                raise Exception("tesseract is not available")

            deepdoctection_analyzer = dd.get_dd_analyzer(
                language=self.__lan__

            )
        self.deepdoctection_analyzer = deepdoctection_analyzer

        dest_model = os.path.join(self.deepdoctection_weights_layout_finale_model_dir, "model_final_inf_only.pt")
        if not os.path.isfile(self.dataset_model_path):
            fake_model_path = os.path.join(
                working_dir,
                "dataset",
                "deepdoctection",
                "weights",
                "layout",
                "d2_model_0829999_layout_inf_only.pt"
            )
            if os.path.isfile(fake_model_path):
                if not os.path.isfile(dest_model):
                    shutil.copy(
                        src=fake_model_path,
                        dst=dest_model
                    )
            # raise FileNotFoundError(f"{self.dataset_model_path} was not found")
        if not os.path.isfile(dest_model):
            print(f"Copy model file form {self.dataset_model_path}\n\tto{dest_model}")

            os.makedirs(self.deepdoctection_weights_layout_finale_model_dir, exist_ok=True)
            shutil.copy(
                src=self.dataset_model_path,
                dst=dest_model
            )
        else:
            print(f"{dest_model} is already")

    def set_langs(self, str_lang: str):
        self.__lan__ = str_lang

    def get_result_from_image(self, img_src: str):
        doc = DocumentFile.from_images(img_src)
        ret = self.get_model(doc)
        return ret

    def get_model(self):
        self.__build__()
        return self.model
