import builtins
import io

import mimetypes
import os.path
import pathlib
import random
import chardet

old_open_file = getattr(builtins, "open")


def cy_open_file(*args, **kwargs):
    is_encrypt = False
    chunk_size = -1
    if kwargs.get("encrypt") == True:
        del kwargs["encrypt"]
        is_encrypt = True
        chunk_size = int(kwargs["chunk_size_in_kb"]) * 1024
        del kwargs["chunk_size_in_kb"]
    wrapper_args = dict(
        file=None,
        mode=None,
        buffering=None,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True
    )
    wrapper_keys = list(wrapper_args.keys())
    send_kwargs = {}
    i = 0
    for x in args:
        try:
            send_kwargs[wrapper_keys[i]] = x
            i += 1
        except:
            return old_open_file(*args, **kwargs)
    send_kwargs = {**send_kwargs, **kwargs}
    file_path = send_kwargs["file"]
    if not isinstance(file_path,str):
        return old_open_file(*args,**kwargs)
    dir_path = pathlib.Path(file_path).parent.__str__()
    file_name = pathlib.Path(file_path).name
    encrypt_info_path = os.path.join(dir_path, file_name + ".cryptor")
    encrypt_info = None
    from cy_file_cryptor.crypt_info import write_dict, read_dict
    if os.path.isfile(encrypt_info_path):
        encrypt_info = read_dict(encrypt_info_path)
        is_encrypt = True

    if is_encrypt:
        if encrypt_info is None:
            encrypt_info = dict(
                chunk_size=chunk_size,
                rotate=random.randint(0, 7)
            )
            write_dict(encrypt_info, encrypt_info_path)
        if send_kwargs.get("mode"):
            if "t" in send_kwargs["mode"]:
                send_kwargs["mode"] = send_kwargs["mode"].replace("t", "b")
            elif "b" not in send_kwargs["mode"]:
                send_kwargs["mode"] = send_kwargs["mode"] + "b"

        ret_fs = old_open_file(**send_kwargs)
        setattr(ret_fs, "cryptor", encrypt_info)
        setattr(ret_fs, "cryptor_rel", encrypt_info_path)
    else:

        ret_fs = old_open_file(*args, **kwargs)
        old_read = getattr(ret_fs,"read")
        def debug_read(*args,**kwargs):
            print(f"{ret_fs.tell()}/{args} {ret_fs.name}")
            return old_read(*args,**kwargs)
        setattr(ret_fs,"read",debug_read)

    setattr(ret_fs, "encrypt", is_encrypt)
    if is_encrypt and isinstance(ret_fs, io.BufferedWriter):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__write__(ret_fs)
        return ret_fs

    if is_encrypt and isinstance(ret_fs,io.BufferedReader):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__read__(ret_fs)
        return ret_fs

    return ret_fs


# # import os
# # os.setxattr("/home/vmadmin/python/cy-py/ai-require.txt", 'user.obfuscator', b'baz')
setattr(builtins, "open", cy_open_file)
# with open("/home/vmadmin/python/cy-py/ai-require.txt", "rb") as fs:
#     txt = fs.read()
#     print(txt)
#
# from PIL import Image
#
# image = Image.open("path/to/your/image.jpg")
