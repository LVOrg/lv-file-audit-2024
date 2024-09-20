import sys
import pathlib
import time
import traceback

from icecream import ic
working_dir= pathlib.Path(__file__).parent.parent.parent.__str__()
sys.path.append("/app")
ic(working_dir)

sys.path.append(working_dir)
import cy_kit
from cyx.common import config
msg = config.get("msg_process") or "ocr-v001"
if not config.get("msg_process"):
    ic("warning: msg_process was not found on startup")
from cy_libs.ocr_files_services import OCRFilesService
svc = cy_kit.single(OCRFilesService)
def main():
    while True:
        try:
            svc.consumer_save_es(msg)
        except:
            svc.logs_to_mongo_db_service.log(
                error_content=traceback.format_exc(),
                url=msg
            )
        finally:
            time.sleep(0.3)
if __name__ == "__main__":
    main()
#docker run -it --entrypoint=/bin/bash -v /mnt/files:/mnt/files -v $(pwd):/app  docker.lacviet.vn/xdoc/lib-ocr-all:38
#python3 cy_jobs/jobs/task_msg_es_update_ocr.py