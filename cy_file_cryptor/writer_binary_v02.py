__footer_size__ = 64
__header_size__ = 1024

import base64
import os
import hashlib

from cy_file_cryptor_verifier.verifier import verify_footer, verify_header


def do_write(fs, data):
    global __footer_size__
    global __header_size__
    from cy_file_cryptor.crypt_info import write_dict
    from cy_file_cryptor import encrypting
    original_close = fs.close
    setattr(fs, "original_close", original_close)
    pos = fs.tell()
    data_size = len(data)
    current_size = pos + data_size
    setattr(fs, "file_size", pos + data_size)

    def modified_close(*args, **kwargs):
        from cy_file_cryptor import writer_binary_comit_v02
        writer_binary_comit_v02.do_commit(fs=fs, header_size=__header_size__, footer_size=__footer_size__)

    # print(f"{pos}->{len(data)}")
    setattr(fs, "close", modified_close)
    fs.cryptor['header'] = fs.cryptor.get('header') or bytes([])
    fs.cryptor['footer'] = fs.cryptor.get('footer') or bytes([])
    if pos == 0:
        fs.cryptor['header'] = data[0:__header_size__]
        fs.cryptor['footer'] = data[__header_size__:][-__footer_size__:]
        remain_data = data[__header_size__:-__footer_size__]
        header_write = os.urandom(len(fs.cryptor['header']))
        # header_write = fs.cryptor['header']
        ret = fs.original_write(header_write)
        ret += fs.original_write(remain_data)
        footer_write = os.urandom(len(fs.cryptor['footer']))
        # footer_write = fs.cryptor['footer']
        ret += fs.original_write(footer_write)

        if pos + len(data) != fs.tell():
            raise Exception()

        return ret



    else:
        header_len = len(fs.cryptor['header'])
        footer_len = len(fs.cryptor['footer'])
        # if footer_len>0:
        #     fs.seek(-footer_len,2)
        #     fs.original_write(fs.cryptor['footer'])
        fs.original_write(data)
        if header_len < __header_size__:
            header_data = (fs.cryptor['header'] + data)[0:__header_size__]
            fs.cryptor['header'] = header_data

        if pos + data_size <= __header_size__:
            """
            Encrypt header if not full
            """
            fs.seek(0)
            header_bytes = fs.cryptor['header']
            header_bytes = os.urandom(len(header_bytes))
            fs.original_write(header_bytes)
        """
        Encrypt footer
        """
        # if len(fs.cryptor['footer'])>__footer_size__:
        #     raise Exception("errror")
        # if len(fs.cryptor['header'])==__header_size__:
        #     if footer_len < __footer_size__:
        #         remain_size = pos+data_size-__header_size__
        #         remain_size = min(-footer_len+__footer_size__, remain_size)
        #         footer_data = data[-remain_size:]
        #         fs.cryptor['footer'] += footer_data
        #
        #
        # footer_bytes = fs.cryptor['footer']
        # # footer_bytes =os.urandom(len(footer_bytes))  #bytes(len(footer_bytes)*0)
        # fs.seek(-len(footer_bytes),2)
        # fs.original_write(footer_bytes)
        # verify_footer(footer_bytes,fs)
