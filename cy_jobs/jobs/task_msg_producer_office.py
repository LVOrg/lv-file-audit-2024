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

__app_name = config.get("app_name") or "all"
msg =config.get("msg_process") or "v-001"
if not config.get("msg_process"):
    ic("warning: msg_process was not found on startup")
from cy_libs.text_files_servcices import ExtractTextFileService
svc = cy_kit.single(ExtractTextFileService)
if __name__ == "__main__":
    while True:
        try:
            apps = svc.get_app_names() if __app_name=="all" else [__app_name]
            for app_name in apps:

                svc.producer_office_content(
                    app_name=app_name,
                    msg = msg
                )
        except:
            raise
        finally:
            time.sleep(0.3)