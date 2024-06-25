__footer_size__ = 64
__header_size__ = 64

import math

__min_wrap_size__ = 1024 * 4
__max_wrap_size__ = 1024 * 8

import base64
import gc
import os
import hashlib
from random import random

# import numpy as np

from random import randint
def do_write(fs, data):
    global __wrap_size__
    from cy_file_cryptor.crypt_info import write_dict
    if fs.cryptor.get("wrap-size") is None:
        wrap_size = randint(__min_wrap_size__, __max_wrap_size__)
    else:
        wrap_size = fs.cryptor.get("wrap-size")
    if fs.cryptor.get("file-size"):
        wrap_size = randint(fs.cryptor.get("file-size")//4, fs.cryptor.get("file-size")//3)
    pos = fs.tell()

    if pos == 0:
        pre_index = fs.cryptor.get('pre-index', 0)
        fs.cryptor['encrypt_block_index'] = 0
        pre_encrypt_block_index = fs.cryptor['encrypt_block_index']
    else:
        pre_index = 0
        pre_encrypt_block_index = fs.cryptor['encrypt_block_index']

    fs_old_len = fs.seek(0, 2)
    fs.seek(pos)
    fs.original_write(data)
    fs_new_len = fs.seek(0, 2)

    if fs_new_len >= wrap_size:
        encrypt_block_index = int(math.floor(fs_new_len / wrap_size))
        for x in range(pre_encrypt_block_index, encrypt_block_index):
            cursor_pos = x * wrap_size
            fs.seek(cursor_pos)
            bff = fs.read(wrap_size)
            if len(bff) < wrap_size:
                print("OK")
            else:
                fs.seek(cursor_pos)
                fs.original_write(bff[::-1])
                # fs.original_write(bff)
            check_len = fs.seek(0, 2)
            if check_len != fs_new_len:
                raise Exception()
        fs.cryptor['encrypt_block_index'] = encrypt_block_index

    check_len = fs.seek(0, 2)

    fs.cryptor['encoding'] = 'binary'
    fs.cryptor["wrap-size"]= wrap_size

    write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file,full_file_size=fs.cryptor.get("file-size"))

