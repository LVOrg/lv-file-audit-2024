import os.path
import uuid

TEM_DIR = None


def __verify_temp_dir__():
    global TEM_DIR
    if TEM_DIR is None:
        raise Exception("Thou should call set_temp_dir before use any method in the package")


def set_temp_dir(dir_path: str):
    global TEM_DIR
    import os
    if os.path.isdir(dir_path):
        TEM_DIR = dir_path
    else:
        os.makedirs(TEM_DIR, exist_ok=True)
        TEM_DIR = dir_path


def new_temp_file(ext: str):
    """
    Create tem directory for processing
    :return:
    """
    global TEM_DIR
    __verify_temp_dir__()
    file_name = str(uuid.uuid4())
    ret = os.path.join(TEM_DIR, f"{file_name}.{ext}")
    return ret


def new_temp_dir():
    """
    Create tem directory for processing
    :return:
    """
    global TEM_DIR
    __verify_temp_dir__()
    dir_name = str(uuid.uuid4())
    ret = os.path.join(TEM_DIR, dir_name)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret
