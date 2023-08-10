"""
Processing file sometime cause some uncontrolled error. Those files are garbage and need to be deleted\n
Xử lý tệp đôi khi gây ra một số lỗi không kiểm soát được. Những tệp đó là rác và cần phải xóa
"""
import os
import pathlib
import sys
from datetime import datetime
from time import sleep
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_kit
from cyx.common.temp_file import TempFiles

tmp_file = cy_kit.singleton(TempFiles)
tmp_dir = tmp_file.get_root_dir()
while True:
    try:
        info = list(os.walk(tmp_dir))
        for root, dir, files in info:
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    print(f"Found {full_path}")
                    mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime = os.stat(full_path)
                    create_on: datetime = datetime.fromtimestamp(atime)
                    days = (datetime.now() - create_on).days
                    if days > 2:
                        os.remove(full_path)
                        print(f"Found {full_path}  was delete")
    except Exception as e:
        print(e)
    sleep(24 * 60 * 60)
