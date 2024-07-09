import builtins
import io

import mimetypes
import os.path
import pathlib
import random
import sys

import chardet
import hashlib



from cy_file_cryptor.crypt_info import write_dict, read_dict

original_open_file = getattr(builtins, "open")
import shutil
import anyio

original_shutil_copy = shutil.copy
original_anyio_open_file = anyio.open_file


def new_shutil_copy(*args, **kwargs):
    print(args)
    print(kwargs)
    return original_open_file(*args, **kwargs)


# setattr(shutil, "copy", new_shutil_copy)


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
    full_file_size = None
    if kwargs.get("encrypt") == True:
        if kwargs.get("file_size") is None:
            raise Exception("file_size keyword was not found")
        del kwargs["encrypt"]
        is_encrypt = True
        chunk_size = int(kwargs.get("chunk_size_in_kb",1024)) * 1024
        full_file_size=  kwargs.get("file_size")
        del kwargs["chunk_size_in_kb"]
        del kwargs["file_size"]
    #open, file, mode, buffering, encoding, errors, newline, closefd, opener
    wrapper_args = dict(
        file=None,
        mode=None,
        buffering=None,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None
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
    if isinstance(file_path,str) and  pathlib.Path(file_path).suffix==".chunks" and os.path.isdir(file_path) and send_kwargs["mode"]=="rb":
        from cy_file_cryptor.reader_chunks import ReadChunksIO
        return ReadChunksIO(dir_path=file_path,original_open_file=original_open_file)
    if isinstance(file_path,str) and file_path.startswith("google-drive://"):
        token=  kwargs.get("token")
        client_id = kwargs.get("client_id")
        client_secret = kwargs.get("client_secret")
        if token is None:
            raise Exception("require token")
        if client_id is None:
            raise Exception("require client_id")
        if client_secret is None:
            raise Exception("require client_secret")
        if send_kwargs.get("mode")=="wb":
            import cy_file_cryptor.google_drive_upload
            ret = cy_file_cryptor.google_drive_upload.create_upload_stream(
                file_path=file_path,
                token = token,
                client_id = client_id,
                client_secret =client_secret
            )
            return ret
        if send_kwargs.get("mode") == "rb":
            import cy_file_cryptor.google_drive_download
            ret = cy_file_cryptor.google_drive_download.create_download_stream(
                file_path=file_path,
                token=token,
                client_id=client_id,
                client_secret=client_secret
            )
            return ret
    if isinstance(file_path,str) and file_path.startswith("mongodb://"):
        from cy_file_cryptor import mongodb_file
        return mongodb_file.do_open(
            url_file= file_path,
            original_open_file=original_open_file,
            *args,**kwargs
        )
    if isinstance(file_path,str) and (file_path.startswith("http://") or file_path.startswith("https://")):
        from cy_file_cryptor.remote_file import do_open
        remote_file_name = kwargs.get("download_filename")
        if not remote_file_name:
            remote_file_name = pathlib.Path(file_path.split('?')[0]).name
        ret = do_open(
            url_file=file_path,
            original_open_file=original_open_file,
            filename=remote_file_name,
            send_kwargs=send_kwargs
        )
        return ret

    file_size = 0
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
    if not isinstance(file_path, str):
        return original_open_file(*args, **kwargs)
    dir_path = pathlib.Path(file_path).parent.__str__()
    file_name = pathlib.Path(file_path).name
    encrypt_info_path = os.path.join(dir_path, file_name + ".cryptor")
    encrypt_info = None

    if os.path.isfile(encrypt_info_path):
        encrypt_info = read_dict(encrypt_info_path, original_open_file,full_file_size=full_file_size)
        is_encrypt = True

    if is_encrypt:
        if encrypt_info is None:
            encrypt_info = dict(
                chunk_size=chunk_size,
                rotate=random.randint(0, 7)
            )
            write_dict(encrypt_info, encrypt_info_path, original_open_file,full_file_size=full_file_size)
        if send_kwargs.get("mode") == "ab":
            send_kwargs["mode"] = "rb+"
            ret_fs = original_open_file(**send_kwargs)
            ret_fs.seek(0, 2)
        else:
            if send_kwargs.get("mode"):
                if "t" in send_kwargs["mode"]:
                    send_kwargs["mode"] = send_kwargs["mode"].replace("t", "b")
                elif "b" not in send_kwargs["mode"]:
                    send_kwargs["mode"] = send_kwargs["mode"] + "b"
            if "a" in send_kwargs["mode"] and encrypt_info["encoding"] != "binary":
                send_kwargs["mode"] = "rb+"
                ret_fs = original_open_file(**send_kwargs)
                ret_fs.seek(0, 2)
            else:
                if "r" not in send_kwargs["mode"] and "+" not in send_kwargs["mode"]:
                    send_kwargs["mode"] += "+"

                ret_fs = original_open_file(**send_kwargs)
        setattr(ret_fs, "cryptor", encrypt_info)
        setattr(ret_fs, "cryptor_rel", encrypt_info_path)
        setattr(ret_fs, "original_open_file", original_open_file)
    else:

        ret_fs = original_open_file(*args, **kwargs)
        def get_size():
            return os.stat(ret_fs.name).st_size
        setattr(ret_fs,"get_size",get_size)


    setattr(ret_fs, "encrypt", is_encrypt)
    setattr(ret_fs, "original_open_file", original_open_file)
    if is_encrypt and isinstance(ret_fs, io.BufferedWriter):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__write__(ret_fs,full_file_size=full_file_size)
        setattr(ret_fs, "old_file_size", file_size)




        return ret_fs
    if is_encrypt and isinstance(ret_fs, io.BufferedRandom):
        import cy_file_cryptor.settings

        cy_file_cryptor.settings.__apply__write__(ret_fs,full_file_size=full_file_size)

        setattr(ret_fs, "old_file_size", file_size)
        def get_size(*args,**kwargs):
            return  ret_fs.old_file_size

        setattr(ret_fs, "get_size", get_size)
        return ret_fs
    if is_encrypt and isinstance(ret_fs, io.BufferedReader):
        import cy_file_cryptor.settings
        cy_file_cryptor.settings.__apply__read__(ret_fs)
        setattr(ret_fs, "old_file_size", file_size)
        def get_size(*args,**kwargs):
            return ret_fs.old_file_size

        setattr(ret_fs, "get_size", get_size)
        ret_fs.cryptor["file-size"] = file_size
        return ret_fs


    return ret_fs


# # import os
# # os.setxattr("/home/vmadmin/python/cy-py/ai-require.txt", 'user.obfuscator', b'baz')
setattr(builtins, "open", cy_open_file)

import _asyncio
from anyio import AsyncFile
async def new_anyio_open_file(file,
    mode: str = "r",
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
    closefd: bool = True,
    opener = None,):
    # fp = await to_thread(
    #     open, file, mode, buffering, encoding, errors, newline, closefd, opener
    # )
    fp = await getattr(anyio.to_thread,"run_sync")(cy_open_file, file, mode, buffering, encoding, errors, newline, closefd, opener)
    return AsyncFile(fp)
    # return await  original_anyio_open_file(*args, **kwargs)


setattr(anyio, "open_file", new_anyio_open_file)



