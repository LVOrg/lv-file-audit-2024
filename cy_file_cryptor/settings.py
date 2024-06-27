__folder__paths__ = {}
__cache__ = {}

import os
import chardet
from cy_file_cryptor.crypt_info import write_dict


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


def __apply__write__(ret_fs,full_file_size):
    if hasattr(ret_fs, "name") and isinstance(ret_fs.name, str):
        if should_encrypt_path(ret_fs.name):
            print(f"{ret_fs.name} should be encrypt")
    old_write = ret_fs.write
    ret_fs.cryptor["file-size"]=full_file_size

    setattr(ret_fs, "original_write", old_write)

    def on_write(*args, **kwargs):
        pos = ret_fs.tell()
        if len(args) == 1:
            from cy_file_cryptor import encrypting

            data = args[0]
            if isinstance(data, str):
                data = data.encode()

            if ret_fs.cryptor.get('encoding') is None:
                detect_data = data[0:ret_fs.cryptor['chunk_size']]
                ret_fs.cryptor['encoding'] = 'binary'
                try:
                    tt =detect_data.decode()
                    del tt
                    ret_fs.cryptor['encoding'] = 'utf8'
                except:
                    ret_fs.cryptor['encoding'] = 'binary'
            if ret_fs.cryptor['encoding'] == 'binary':
                from cy_file_cryptor import writer_binary_v02
                return writer_binary_v02.do_write(
                    fs=ret_fs,
                    data=data
                )

            else:
                from cy_file_cryptor import writer_text
                return writer_text.do_write(
                    fs=ret_fs,
                    data=data
                )

    def on_writelines(*args, **kwargs):
        text = "\n".join(args[0])
        ret = ret_fs.write(text)
        return ret

    setattr(ret_fs, "write", on_write)
    setattr(ret_fs, "writelines", on_writelines)


def __apply__read__(ret_fs):
    old_read = ret_fs.read
    setattr(ret_fs, "original_read", old_read)

    def on_read(*args, **kwargs):


        if ret_fs.cryptor.get('encoding','binary') == 'binary':
            from cy_file_cryptor import reader_binary_v02
            return reader_binary_v02.do_read(
                ret_fs,
                *args,
                **kwargs
            )

        else:
            from cy_file_cryptor import reader_text
            return reader_text.do_read(
                ret_fs,
                *args,
                **kwargs)

    setattr(ret_fs, "read", on_read)

    # 1622 /0.472

    return ret_fs
