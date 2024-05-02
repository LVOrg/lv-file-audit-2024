import os
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import threading
import uuid

import cy_kit
from cyx.common import config
from cyx.repository import Repository

from cyx.google_drive_utils.directories import GoogleDirectoryService
svc= cy_kit.singleton(GoogleDirectoryService)
# tolal,_,lst =svc.get_all_folders("lv-docs")
# for x in lst:
#     print(x)
# ret=svc.check_folder_structure(app_name="lv-docs",directory_path=["long-test"])
def run():
    id=svc.create_folders(app_name="lv-docs",directory_path = f"2024/05/01/{uuid.uuid4()}")
    print(id)
lst = []
for i in range(30):
    th1 = threading.Thread(target=run)
    lst.append(th1)
for x in lst:
    x.start()
for x in lst:
    x.join()
