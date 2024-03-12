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

import numpy as np

from random import randint
def do_write(fs, data):
    global __wrap_size__
    from cy_file_cryptor.crypt_info import write_dict
    if fs.cryptor.get("wrap-size") is None:
        wrap_size = randint(__min_wrap_size__, __max_wrap_size__)
    else:
        wrap_size = fs.cryptor.get("wrap-size")

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

    if fs_new_len > wrap_size:
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
        print("encrypt")
    check_len = fs.seek(0, 2)
    # if check_len != fs_new_len:
    #     raise Exception()
    # index = int(math.floor(fs_old_len / wrap_size))
    # remain_size_in_file = fs_old_len-index*wrap_size
    # fs.cryptor['pre-index'] = index
    # ret = fs.original_write(data)
    # fs_new_len = fs.seek(0,2)
    #
    #
    # if index>1:
    #     for x in range(pre_index, index):
    #         cursor_pos = x * wrap_size
    #         fs.seek(cursor_pos)
    #         bff = fs.read(wrap_size)
    #         fs.original_write(bff[::-1])
    fs.cryptor['encoding'] = 'binary'
    fs.cryptor["wrap-size"]= wrap_size
    # fs.cryptor["file-size"] = fs.file_size
    write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
    # data_size = pos + len(data)
    #
    # ret = fs.original_write(data[::-1])
    # fs_len = fs.seek(0, 2)
    #
    # index = int(math.floor(fs_len / wrap_size))
    #
    # if fs_len % wrap_size > 0:
    #     if index > 0:
    #         raise Exception()
    # # ret = 0
    # # if data_size > wrap_size:
    # #     remain_size = wrap_size - pos
    # #     remain_data = data[0:remain_size]
    # #     prefix_data = data[remain_size:]
    # #     fs.original_write(remain_data)
    # #     n = int(math.floor(data_size / wrap_size))
    # #     if data_size % wrap_size>0:
    # #         n+=1
    # #     fs.seek(-wrap_size, 2)
    # #     fs.original_write(prefix_data)
    # #
    # # else:
    # #     ret = fs.original_write(data[::-1])
    #
    # return fs.seek(0, 2)


def do_write_2(fs, data):
    e_data = np.frombuffer(data, dtype=np.uint8)
    e_data = ~e_data
    ret = fs.original_write(e_data.tobytes())
    del e_data
    del data
    gc.collect()
    return ret


def do_write_1(fs, data):
    global __footer_size__
    global __header_size__
    from cy_file_cryptor.crypt_info import write_dict
    from cy_file_cryptor import encrypting

    def modified_close(*args, **kwargs):
        from cy_file_cryptor import writer_binary_comit_v02
        writer_binary_comit_v02.do_commit(fs=fs, header_size=__header_size__, footer_size=__footer_size__)

    original_close = fs.close
    setattr(fs, "original_close", original_close)
    setattr(fs, "close", modified_close)
    pos = fs.tell()
    data_size = len(data)
    current_size = pos + data_size
    if pos == 0:
        fs.cryptor['header'] = bytes([])
        fs.cryptor['footer'] = bytes([])
        fs.cryptor['footer_size'] = len(fs.cryptor['footer'])
        fs.cryptor['header_size'] = len(fs.cryptor['header'])

    else:
        fs.cryptor['header'] = fs.cryptor.get('header') or bytes([])
        fs.cryptor['footer'] = fs.cryptor.get('footer') or bytes([])
    if len(fs.cryptor['footer']) > 0:
        print("XX")
    """
    Restore original content
    """
    # fs.seek(0)
    # fs.original_write(fs.cryptor['header'])
    # fs.seek(-len(fs.cryptor['footer']),2)
    # fs.original_write(fs.cryptor['footer'])
    fs.seek(0)
    check_header = fs.read(len(fs.cryptor['header']))
    if check_header != fs.cryptor['header']:
        raise Exception()
    if len(fs.cryptor['footer']) > 0:
        fs.seek(-len(fs.cryptor['footer']), 2)
        fs.original_write(fs.cryptor['footer'])
    fs.seek(pos)
    """Write new content"""
    fs.original_write(data)
    file_zie = fs.seek(0, 2)

    if file_zie != current_size:
        raise Exception()
    body_size = current_size - __footer_size__ - __header_size__
    new_footer_size = current_size - __header_size__
    """Encrypt header and footer"""
    remain_data = data
    if len(fs.cryptor['header']) + len(data[0:__header_size__]) > __header_size__:
        remain_header_size = __header_size__ - len(fs.cryptor['header'])
        fs.cryptor['header'] += data[0:remain_header_size]
        remain_data = data[remain_header_size:]
    else:
        fs.cryptor['header'] += data[0:__header_size__]
        remain_data = data[__header_size__:]
    remain_footer_size = __footer_size__ - len(fs.cryptor['footer'])
    next_footer_data = remain_data[-__footer_size__:]

    fs.cryptor['footer'] += next_footer_data[0:remain_footer_size]
    # if len(fs.cryptor['footer'])>0:
    #     fs.seek(-len(fs.cryptor['footer']),2)
    #     fs.original_write(fs.cryptor['footer'])
    if len(fs.cryptor['footer']) > __footer_size__:
        raise Exception()
    # if len(fs.cryptor['footer']) + len(next_footer_data) > __footer_size__:
    #     remain_footer_size = __header_size__ - len(fs.cryptor['footer'])
    #     fs.cryptor['footer'] += data[0:remain_footer_size]
    # else:
    #     fs.cryptor['footer'] += data[__header_size__:][0:new_footer_size]

    fs.seek(0)
    header_in_file = fs.read(len(fs.cryptor['header']))
    if header_in_file != fs.cryptor['header']:
        raise Exception("Check sum header error")
    fs.seek(-len(fs.cryptor['footer']), 2)
    footer_in_file = fs.read()
    fs.cryptor['footer'] = footer_in_file
    fs.seek(-len(fs.cryptor['footer']), 2)
    fs.original_write(os.urandom(len(fs.cryptor['footer'])))
