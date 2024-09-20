import sys
import pathlib
import time
from icecream import ic
working_dir= pathlib.Path(__file__).parent.parent.parent.__str__()
ic(working_dir)

sys.path.append(working_dir)
sys.path.append("/app")
import cy_kit
from cyx.common import config
msg =config.get("msg_process") or "ocr-v001"
if not config.get("msg_process"):
    ic("warning: msg_process was not found on startup")
from cy_libs.ocr_files_services import OCRFilesService


def main():
    svc = cy_kit.single(OCRFilesService)
    while True:
        try:
            svc.consumer_ocr_content(msg)
        except:
            raise
        finally:
            time.sleep(0.3)
if __name__ == "__main__":
    main()
