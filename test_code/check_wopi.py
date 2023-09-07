import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from cy_wopi_util import wopi_discovery

app = wopi_discovery.get_app("excel")
action = wopi_discovery.get_action("word","edit","docx")
url = wopi_discovery.get_action_url(
    app_name="word",
    action="view",
    ext_file="docx",
    wopi_source="https://codx.lacviet.vn/lvfile/api/default/file/ff7a6afb-ad73-4753-aa49-f728b455a7c7/dms_api_bo%20sung_.docx")
print(url)