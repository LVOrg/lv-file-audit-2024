import pathlib
import sys
import time

from icecream import ic

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
from cyx.common import config
__app_name = config.get("app_name") or "all"
msg = config.get("msg_process") or "ocr-v001"
import cy_kit
from cy_libs.ocr_files_services import OCRFilesService

def main():
    svc = cy_kit.singleton(OCRFilesService)
    while True:
        try:
            apps = svc.get_app_names() if __app_name == "all" else [__app_name]

            for app_name in apps:
                svc.producer_ocr_content(
                    app_name=app_name,
                    msg=msg
                )
        except:
            raise
        finally:
            time.sleep(0.7)




if __name__ == "__main__":
    main()

#docker run -it --entrypoint=/bin/bash -v /mnt/files:/mnt/files -v $(pwd):/app  docker.lacviet.vn/xdoc/lib-ocr-all:37
#python3 cy_jobs/jobs/task_msg_producer_ocr.py