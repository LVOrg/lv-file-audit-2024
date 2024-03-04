__folder__paths__ = {}
__cache__ = {}

import os
import chardet


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
    if hasattr(ret_fs, "name") and isinstance(ret_fs.name, str):
        if should_encrypt_path(ret_fs.name):
            print(f"{ret_fs.name} should be encrypt")
    if hasattr(ret_fs, "close") and callable(ret_fs.close):

        old_write = ret_fs.write

        def on_write(*args, **kwargs):
            pos = ret_fs.tell()
            if len(args) == 1:
                from cy_file_cryptor import encrypting

                data = args[0]
                if isinstance(data, str):
                    data = data.encode()
                detect_data = data[0:100]
                result = chardet.detect(detect_data)
                print(result.get("encoding"))

                encrypt_bff = encrypting.rotate_bit_left(
                    data_encrypt=data,
                    chunk_size=ret_fs.cryptor["chunk_size"],
                    rota=ret_fs.cryptor['rotate'])
                for x in encrypt_bff:
                    old_write(x)

        if hasattr(ret_fs, "cryptor") and isinstance(ret_fs.cryptor, dict):

            if hasattr(ret_fs, "mode") and 'w' in ret_fs.mode:
                setattr(ret_fs, "write", on_write)

    # 1622 /0.472

    return ret_fs
