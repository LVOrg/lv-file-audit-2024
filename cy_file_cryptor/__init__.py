import builtins
import io




old_open_file = getattr(builtins, "open")


def cy_open_file(*args, **kwargs):
    # wrapper_args = dict(
    #     file=None,
    #     mode=None,
    #     buffering=None,
    #     encoding=None,
    #     errors=None,
    #     newline=None,
    #     closefd=True
    # )
    # wrapper_keys = list(wrapper_args.keys())
    # send_kwargs = {}
    # i = 0
    # for x in args:
    #     send_kwargs[wrapper_keys[i]] = x
    #     i += 1
    #
    # send_kwargs = {**send_kwargs, **kwargs}

    ret_fs = old_open_file(*args, **kwargs)
    import cy_file_cryptor.settings
    cy_file_cryptor.settings.apply(ret_fs)
    if isinstance(ret_fs, io.TextIOWrapper):
        from cy_file_cryptor.modifier_text_io_wrapper import text_io_wrapper
        ret_fs = text_io_wrapper(ret_fs)
        return ret_fs
    elif isinstance(ret_fs, io.BufferedReader):
        from cy_file_cryptor.modifier_buffered_reader import buffered_reader
        ret = buffered_reader(ret_fs)
        return ret
    elif isinstance(ret_fs, io.BufferedWriter):
        from cy_file_cryptor.modifier_buffered_writer import buffer_writer
        ret = buffer_writer(ret_fs)
        return ret
    else:
        raise Exception(f"{type(ret_fs)} was not implement")


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
