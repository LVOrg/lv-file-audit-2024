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

def get_content_from_viet_ocr(pdf_file):
    from cy_lib_ocr.ocr_services import OCRService
    svc = cy_kit.singleton(OCRService)
    return svc.get_content_from_pdf(pdf_file)

def main():
    svc = cy_kit.single(OCRFilesService)
    svc.set_pre_post(get_content_from_viet_ocr)
    while True:
        try:
            svc.consumer_ocr_content(msg)
        except:
            raise
        finally:
            time.sleep(0.3)
if __name__ == "__main__":
    main()
#docker run -it --entrypoint=/bin/bash -v /mnt/files:/mnt/files -v $(pwd):/app  docker.lacviet.vn/xdoc/lib-ocr-all:37
#python3 cy_jobs/jobs/task_msg_consumer_ocr.py