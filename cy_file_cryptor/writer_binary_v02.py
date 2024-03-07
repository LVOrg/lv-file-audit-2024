__footer_size__ = 64
__header_size__ = 64

import base64
import os


def do_write(fs,data):
    global __footer_size__
    global __header_size__
    from cy_file_cryptor.crypt_info import write_dict
    from cy_file_cryptor import encrypting
    original_close = fs.close
    setattr(fs,"original_close",original_close)
    pos = fs.tell()
    data_size = len(data)
    def modified_close(*args,**kwargs):

        fs.original_close(*args,**kwargs)
        with  fs.original_open_file(fs.name,"rb+") as fse:
            fse.seek(-__footer_size__,2)
            footer_data = fse.read()
            fse.seek(-__footer_size__, 2)
            fse.write(os.urandom(__footer_size__))
            encrypt_bff = encrypting.encrypt_content(
                data_encrypt=footer_data,
                chunk_size=__footer_size__,
                rota=fs.cryptor['rotate'],
                first_data=footer_data[0])
            fs.cryptor['footer'] = base64.b64encode(next(encrypt_bff)).decode("utf-8")
            fs.cryptor['footer-first'] = footer_data[0]
            fs.cryptor['encoding'] = 'binary'
            fs.cryptor["file-size"] = os.path.getsize(fs.name)
            write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
        print("ok")
    setattr(fs,"close",modified_close)
    if pos<__header_size__:
        fs.original_write(os.urandom(__footer_size__))
        fs.original_write(data[pos+__header_size__:])
        encrypt_bff = encrypting.encrypt_content(
            data_encrypt= data[0:__header_size__],
            chunk_size=__header_size__,
            rota= fs.cryptor['rotate'],
            first_data=data[0])
        fs.cryptor['header'] = base64.b64encode(next(encrypt_bff)).decode("utf-8")
        fs.cryptor['header-first'] = data[0]

    else:
        fs.original_write(data)

    # if not hasattr(fs,"header_cryptor"):
    #     setattr(fs,"header_cryptor",bytes([]))
    # pos = fs.tell()
    # data_size = len(data)
    # if pos<__header_size__:
    #     fs.header_cryptor+=data
    #     fs.original_write(__header_size__*"0".encode())
    #     if pos+data_size> __header_size__:
    #         fs.original_write(data[__header_size__:])
    #
    # else:
    #     fx=1
    # ret = 0

    # chunk_size = fs.cryptor['chunk_size']
    # data_size = len(data)
    # if data_size>chunk_size:
    #     if pos == 0:
    #
    #         fs.cryptor['first-data'] = data[0]
    #         fs.cryptor['encoding'] = 'binary'
    #         write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
    #         encrypt_bff = encrypting.encrypt_content(
    #             data_encrypt= data[0:chunk_size],
    #             chunk_size=chunk_size,
    #             rota= fs.cryptor['rotate'],
    #             first_data=data[0])
    #         ret += fs.original_write(next(encrypt_bff))
    #         ret += fs.original_write(data[fs.cryptor['chunk_size']:])
    #     else:
    #         ret += fs.original_write(data)
    #     return ret
    # else:
    #     return bytes([])