import builtins
import io

import mimetypes
import os.path
import pathlib
import random
import chardet
import hashlib
from cy_file_cryptor.crypt_info import write_dict, read_dict
original_open_file = getattr(builtins, "open")
def hash_file(filename, hash_function=hashlib.sha256):
    """
    Calculates the hash of a file using a specified hash function.

    Args:
        filename (str): Path to the file.
        hash_function (callable, optional): The hash function to use. Defaults to sha256.

    Returns:
        str: The hexadecimal representation of the hash digest.
    """

    # Open the file in binary read mode
    with original_open_file(filename, 'rb') as file:
        # Create a hash object for the chosen function
        hasher = hash_function()

        # Read the file content in chunks (more efficient for large files)
        chunk_size = 65536  # Adjust chunk size as needed
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

        # Get the final hash digest
        digest = hasher.hexdigest()

    return digest

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
            return original_open_file(*args, **kwargs)
    send_kwargs = {**send_kwargs, **kwargs}

    file_path = send_kwargs["file"]
    file_size = 0
    if os.path.isfile(file_path):
        file_size= os.path.getsize(file_path)
    if not isinstance(file_path,str):
        return original_open_file(*args, **kwargs)
    dir_path = pathlib.Path(file_path).parent.__str__()
    file_name = pathlib.Path(file_path).name
    encrypt_info_path = os.path.join(dir_path, file_name + ".cryptor")
    encrypt_info = None

    if os.path.isfile(encrypt_info_path):
        encrypt_info = read_dict(encrypt_info_path, original_open_file)
        is_encrypt = True

    if is_encrypt:
        if encrypt_info is None:
            encrypt_info = dict(
                chunk_size=chunk_size,
                rotate=random.randint(0, 7)
            )
            write_dict(encrypt_info, encrypt_info_path, original_open_file)
        if send_kwargs.get("mode")=="ab":
            send_kwargs["mode"]="rb+"
            ret_fs = original_open_file(**send_kwargs)
            ret_fs.seek(0, 2)
        else:
            if send_kwargs.get("mode"):
                if "t" in send_kwargs["mode"]:
                    send_kwargs["mode"] = send_kwargs["mode"].replace("t", "b")
                elif "b" not in send_kwargs["mode"]:
                    send_kwargs["mode"] = send_kwargs["mode"] + "b"
            if "a" in send_kwargs["mode"] and encrypt_info["encoding"]!="binary":
                send_kwargs["mode"] = "rb+"
                ret_fs = original_open_file(**send_kwargs)
                ret_fs.seek(0, 2)
            else:
                if "r" not in send_kwargs["mode"] and "+" not in send_kwargs["mode"]:
                    send_kwargs["mode"]+="+"

                ret_fs = original_open_file(**send_kwargs)
        setattr(ret_fs, "cryptor", encrypt_info)
        setattr(ret_fs, "cryptor_rel", encrypt_info_path)
        setattr(ret_fs,"original_open_file",original_open_file)
    else:

        ret_fs = original_open_file(*args, **kwargs)


    setattr(ret_fs, "encrypt", is_encrypt)
    setattr(ret_fs, "original_open_file", original_open_file)
    if is_encrypt and isinstance(ret_fs, io.BufferedWriter):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__write__(ret_fs)
        setattr(ret_fs, "old_file_size", file_size)
        return ret_fs
    if is_encrypt and isinstance(ret_fs, io.BufferedRandom):
        import cy_file_cryptor.settings

        cy_file_cryptor.settings.__apply__write__(ret_fs)
        setattr(ret_fs, "old_file_size", file_size)
        return ret_fs
    if is_encrypt and isinstance(ret_fs,io.BufferedReader):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__read__(ret_fs)
        setattr(ret_fs,"old_file_size",file_size)
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
