import os.path
import pathlib
import time
import pymongo
_wrking_dir_ = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(_wrking_dir_)

from cyx.media.pdf import PDFService
from cyx.common.temp_file import TempFiles
import cy_kit
instance =cy_kit.singleton(PDFService)
print(sys.modules[ instance.get_image.__module__])
ocr_file_test = f"/app/docker-debian/test-ocr.pdf"
ocr_file = instance.ocr(
                pdf_file=ocr_file_test,

            )
temp_file = cy_kit.singleton(TempFiles)
ret = temp_file.move_file(
            from_file=ocr_file,
            app_name="app-test",
            sub_dir="pdf-ocr"
        )
print("test ocr is ok")
print(f"{ocr_file} is out put")
print(f"Move {ocr_file} to {ret}")

time.sleep(30)