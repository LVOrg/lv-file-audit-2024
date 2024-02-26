import builtins
import io

from cy_file_criptor.cy_text_io_wrapper import CyTextIOWrapper
from cy_file_criptor.cy_buffered_reader import CyBufferedReader

old_open_file = getattr(builtins, "open")


def cy_open_file(*args, **kwargs):
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

    ret_fs = old_open_file(**send_kwargs)
    if isinstance(ret_fs, io.TextIOWrapper):
        ret = CyTextIOWrapper(ret_fs)
        return ret
    elif isinstance(ret_fs, io.BufferedReader):
        ret = CyBufferedReader(ret_fs)
        return ret
    else:
        raise Exception(f"{type(ret_fs)} was not implement")


# import os
# os.setxattr("/home/vmadmin/python/cy-py/ai-require.txt", 'user.obfuscator', b'baz')
setattr(builtins, "open", cy_open_file)
with open("/home/vmadmin/python/cy-py/ai-require.txt", "rb") as fs:
    txt = fs.read()
    print(txt)

from PIL import Image

image = Image.open("path/to/your/image.jpg")
