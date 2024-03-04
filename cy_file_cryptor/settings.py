__folder__paths__ = {}
__cache__ = {}


def set_encrypt_folder_path(directory: str):
    global __folder__paths__
    __folder__paths__[directory.lower()] = 1


def should_encrypt_path(file_path: str):
    global __cache__
    global __folder__paths__
    if __cache__.get(file_path.lower()):
        return True
    else:
        for k, v in __folder__paths__.items():
            if file_path.lower().startswith(k):
                __cache__[file_path.lower()] = file_path
                return True
        return False


def apply(ret_fs):
    if hasattr(ret_fs,"name") and isinstance(ret_fs.name,str):
        if should_encrypt_path(ret_fs.name):
            print(f"{ret_fs.name} should be encrypt")
    return ret_fs