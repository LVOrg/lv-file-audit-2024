import base64
import datetime
import gc
import json
import os.path
import threading
import uuid
import numpy as np


pre_fix_cache_key = "2930dbae-f443-435f-b6a1-2553c0a2bc7d"


def write_dict(data: dict, file_path, original_open,full_file_size=None):
    """
    Version 2 fix file too  small
    :param data:
    :param file_path:
    :param original_open:
    :return:
    """
    from cy_file_cryptor import context
    data["file-size"]=full_file_size

    context.write_to_cache(f"{pre_fix_cache_key}/{file_path}", data)

    # global __buffer_cache__
    # __buffer_cache__[file_path] = data

    def __save_file__():
        with original_open(file_path, "wb") as fs:
            txt_json = json.dumps(data)
            data_json = np.frombuffer(txt_json.encode(), dtype=np.uint8)
            data_json = ~data_json
            fs.write(data_json.tobytes())

    threading.Thread(target=__save_file__, args=()).start()


def clear_cache(file_path):
    from cy_file_cryptor import context
    ret = context.clear_cache(f"{pre_fix_cache_key}/{file_path}")
    return ret
def read_dict(file_path, original_open,full_file_size) -> dict:
    from cy_file_cryptor import context
    ret = context.read_from_cache(f"{pre_fix_cache_key}/{file_path}")
    if isinstance(ret, dict):
        if full_file_size and  ret.get("wrap-size",0)>full_file_size:
            ret["wrap-size"]=full_file_size
        return ret
    else:
        with original_open(file_path, "rb") as f:
            data = f.read()
            data_json = np.frombuffer(data, dtype=np.uint8)
            data_json = ~data_json
            ret = json.loads(data_json.tobytes().decode())
            context.write_to_cache(f"{pre_fix_cache_key}/{file_path}",ret)
        if full_file_size and ret["wrap-size"]>full_file_size:
            ret["wrap-size"]=full_file_size
        return ret


