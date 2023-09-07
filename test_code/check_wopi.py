import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
from cy_wopi_util import wopi_discovery

app = wopi_discovery.get_app("excel")
action = wopi_discovery.get_action("word","edit","docx")
print(list(action.keys()))