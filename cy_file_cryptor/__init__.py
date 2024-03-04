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
    if kwargs.get("encrypt")==True:
        del  kwargs["encrypt"]
        is_encrypt = True
        chunk_size = int(kwargs["chunk_size_in_kb"])*1024
        del  kwargs["chunk_size_in_kb"]
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
        send_kwargs[wrapper_keys[i]] = x
        i += 1

    send_kwargs = {**send_kwargs, **kwargs}


    if is_encrypt:

        if send_kwargs.get("mode"):
            if "t" in send_kwargs["mode"]:
                send_kwargs["mode"]=send_kwargs["mode"].replace("t","b")
            else:
                send_kwargs["mode"] = send_kwargs["mode"]+"b"
        file_path = send_kwargs["file"]
        dir_path = pathlib.Path(file_path).parent.__str__()
        file_name = pathlib.Path(file_path).name
        encrypt_info_path = os.path.join(dir_path,file_name+".cryptor")
        from cy_file_cryptor.crypt_info import write_dict,read_dict
        if os.path.isfile(encrypt_info_path):
            info = read_dict(encrypt_info_path)
        else:
            info = dict(
                chunk_size=chunk_size,
                rotate = random.randint(0,7)
            )
            write_dict(info,encrypt_info_path)


        ret_fs = old_open_file(**send_kwargs)
        setattr(ret_fs,"cryptor",info)
    else:
        ret_fs = old_open_file(*args, **kwargs)
    setattr(ret_fs,"encrypt",is_encrypt)
    if is_encrypt and isinstance(ret_fs, io.BufferedWriter):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.apply(ret_fs)
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
