import math

import numpy as np


def __decode_data__(data, start_pos, chunk_size):
    bff = data[start_pos:chunk_size]
    while bff:
        if len(bff) < chunk_size:
            yield bff
        else:
            yield bff[::-1]
            # yield bff

        start_pos += chunk_size
        bff = data[start_pos:start_pos + chunk_size]


def do_read(fs, *args, **kwargs):
    block_size = 1024 * 4
    bff = None
    if len(args) == 0:
        pos = fs.tell()
        data = fs.original_read(*args, **kwargs)
        ret = bytes([])
        iter_data = __decode_data__(data, pos, block_size)
        for x in iter_data:
            ret += x

        return ret
    else:

        pos = fs.tell()

        read_len = args[0]
        start_block_pos = (pos // block_size) * block_size
        end_block_pos = start_block_pos + block_size
        fs.seek(start_block_pos)
        bff = fs.original_read(block_size)
        if len(bff) == block_size:
            bff = bff[::-1]
        ret_data = bff[pos - start_block_pos:pos - start_block_pos + read_len]
        remain_len = read_len-len(ret_data)
        while remain_len>0:
            next_block=start_block_pos+block_size
            next_pos = fs.tell()
            next_data = fs.original_read(block_size)
            if len(next_data)<block_size:
                tmp_next = next_data[0:remain_len]
                ret_data+=tmp_next
                break
            else:
                tmp_next = next_data[::-1][0:remain_len]
                ret_data+=tmp_next
            remain_len-=len(tmp_next)
        #     p=fs.tell()
        #     print(p)


        fs.seek(pos+read_len)
        return ret_data



def do_read_beta(fs, *args, **kwargs):
    data = fs.original_read(*args, **kwargs)
    e_data = np.frombuffer(data, dtype=np.uint8)
    e_data = ~e_data
    return e_data.tobytes()


def do_read_1(fs, *args, **kwargs):
    from cy_file_cryptor import encrypting
    pos = fs.tell()
    fs.cryptor['header'] = fs.cryptor.get('header') or bytes([])
    fs.cryptor['footer'] = fs.cryptor.get('footer') or bytes([])
    header_len = len(fs.cryptor['header'])
    footer_len = len(fs.cryptor['footer'])
    file_size = fs.cryptor["file-size"]
    if len(args) == 0:
        if pos == 0:
            """
            Read all data from the first
            """
            ret_data = fs.original_read(*args, **kwargs)

            if footer_len > 0:
                return fs.cryptor['header'] + ret_data[header_len:-footer_len] + fs.cryptor['footer']
            else:
                return fs.cryptor['header'] + ret_data[header_len:]
        else:
            """
            read all data from position
            """
            if pos < header_len:
                """
                if pos less than  header_len
                return data in header
                """
                return fs.cryptor['header'][:pos]
            elif pos < file_size - footer_len:
                """
                is still being original data
                """
                ret_data = fs.original_read(*args, **kwargs)
                return fs.cryptor['header'][pos:] + ret_data[header_len:-footer_len] + fs.cryptor['footer']
            else:
                return fs.cryptor['footer'][pos:]
    else:
        read_size = args[0]
        if pos + read_size < header_len:
            """
            data will read be in header
            """
            fs.seek(pos + read_size)
            return fs.cryptor['header'][pos:pos + read_size]
        elif pos + read_size < file_size - footer_len:
            ret_data = fs.original_read(*args, **kwargs)
            ret = fs.cryptor['header'][pos:]
            ret += ret_data[len(ret):]
            return ret

        else:
            ret_data = fs.original_read(*args, **kwargs)
            if ret_data:
                limit = file_size - footer_len - pos
                limit2 = file_size - pos - limit
                ret = ret_data[:limit] + fs.cryptor['footer'][:limit2]
                if pos > header_len:
                    return ret
                else:
                    return fs.cryptor['header'] + ret[header_len:]
            else:
                return ret_data
