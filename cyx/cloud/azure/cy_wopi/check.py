import cy_kit
from cyx.cy_wopi.wopi_discovery import get_discovery,get_hash_discovery
data = get_discovery(nocache=True)
data_app = get_hash_discovery(nocache=True)
print(data)