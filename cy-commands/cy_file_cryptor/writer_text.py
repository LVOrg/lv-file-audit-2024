import gc

import numpy as np


def do_write(fs, data):
    from cy_file_cryptor.crypt_info import write_dict
    from cy_file_cryptor import encrypting
    from cy_file_cryptor.encrypting import print_bytes
    np_data = np.frombuffer(data, dtype=np.uint8)
    np_data = ~ np_data
    ret = fs.original_write(np_data.tobytes())
    del np_data
    gc.collect()
    fs.cryptor['encoding'] = "utf-8"
    write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
    return ret
    # pos= fs.tell()
    # if pos == 0:
    #     fs.cryptor['first-data'] = data[0]
    #     fs.cryptor['last-data'] = data[-1]
    #     fs.cryptor['encoding'] = "utf-8"
    #     write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
    #
    # if pos > 0:
    #     from cy_file_cryptor.encrypting import print_bytes
    #     fs.seek(pos - 1)
    #     last_byte = fs.read(1)[0]
    #
    #     first_append = data[0]
    #     first_bit = (first_append >> 7)
    #     last_byte = last_byte | first_bit
    #     fs.seek(pos - 1)
    #     fs.original_write(bytes([last_byte]))
    #
    # encrypt_bff = encrypting.encrypt_content(
    #     data_encrypt=data,
    #     chunk_size= fs.cryptor["chunk_size"],
    #     rota=fs.cryptor['rotate'],
    #     first_data=fs.cryptor['first-data'])
    # ret = None
    # for x in encrypt_bff:
    #     ret = fs.original_write(x)
    # return ret
