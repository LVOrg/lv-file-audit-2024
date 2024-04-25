import threading
import uuid

import cy_kit
from cyx.common import config
from cyx.repository import Repository

from cyx.google_drive_utils.directories import GoogleDirectoryService
svc= cy_kit.singleton(GoogleDirectoryService)
# ret=svc.check_folder_structure(app_name="lv-docs",directory_path=["long-test"])
def run():
    id=svc.create_folders(app_name="lv-docs",directory_path = f"2024/04/14/{uuid.uuid4()}")
    print(id)
th1 = threading.Thread(target=run)
th2 = threading.Thread(target=run)
th1.start()
th2.start()
th1.join(1)
th2.join(1)