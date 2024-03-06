__folder__paths__ = {}
__cache__ = {}

import os
import chardet
from cy_file_cryptor.crypt_info import write_dict

def set_encrypt_folder_path(directory: str):
    global __folder__paths__
    __folder__paths__[directory.lower()] = 1


def should_encrypt_path(file_path: str):
    global __cache__
    global __folder__paths__
    if __cache__.get(file_path.lower()):
        return True
    else:
        for k, v in __folder__paths__.items():
            if file_path.lower().startswith(k):
                __cache__[file_path.lower()] = file_path
                return True
        return False


def __apply__write__(ret_fs):
    if hasattr(ret_fs, "name") and isinstance(ret_fs.name, str):
        if should_encrypt_path(ret_fs.name):
            print(f"{ret_fs.name} should be encrypt")
    old_write = ret_fs.write

    def on_write(*args, **kwargs):
        pos = ret_fs.tell()
        if len(args) == 1:
            from cy_file_cryptor import encrypting

            data = args[0]
            if isinstance(data, str):
                data = data.encode()
            detect_data = data[0:ret_fs.cryptor['chunk_size']]
            result = chardet.detect(detect_data)
            if result.get("encoding") is None or ("utf" not in result.get("encoding") and "ascii" not in result.get("encoding")):
                ret=0
                if pos ==0:

                    ret_fs.cryptor['first-data'] = data[0]
                    ret_fs.cryptor['encoding'] = 'binary'
                    write_dict(ret_fs.cryptor, ret_fs.cryptor_rel,ret_fs.original_open_file)
                    encrypt_bff = encrypting.encrypt_content(
                        data_encrypt=detect_data,
                        chunk_size=len(detect_data),
                        rota=ret_fs.cryptor['rotate'],
                        first_data=detect_data[0])
                    ret+=old_write(next(encrypt_bff))
                    ret+=old_write(data[ret_fs.cryptor['chunk_size']:])
                else:
                    ret+=old_write(data)
                return ret

            if pos == 0:

                ret_fs.cryptor['first-data'] = data[0]
                ret_fs.cryptor['last-data'] = data[-1]
                ret_fs.cryptor['encoding']="utf-8"
                write_dict(ret_fs.cryptor, ret_fs.cryptor_rel,ret_fs.original_open_file)
            first_data = ret_fs.cryptor['first-data']
            if pos>0:
                from cy_file_cryptor.encrypting import print_bytes
                ret_fs.seek(pos-1)
                last_byte = ret_fs.read(1)[0]

                first_append = data[0]
                first_bit = (first_append>>7)
                last_byte =last_byte |first_bit
                ret_fs.seek(pos - 1)
                old_write(bytes([last_byte]))



            encrypt_bff = encrypting.encrypt_content(
                data_encrypt=data,
                chunk_size=ret_fs.cryptor["chunk_size"],
                rota=ret_fs.cryptor['rotate'],
                first_data=ret_fs.cryptor['first-data'])
            ret = None
            for x in encrypt_bff:
                ret = old_write(x)
            return  ret
    def on_writelines(*args,**kwargs):
        text ="\n".join(args[0])
        ret =ret_fs.write(text)
        return ret

    setattr(ret_fs, "write", on_write)
    setattr(ret_fs,"writelines",on_writelines)


def __apply__read__(ret_fs):
    old_read = ret_fs.read

    def on_read(*args, **kwargs):
        from cy_file_cryptor import encrypting
        pos = ret_fs.tell()




        if ret_fs.cryptor['encoding']=='binary':
            if pos<ret_fs.cryptor["chunk_size"]:
                if len(args)==0:
                    data = old_read(*args, **kwargs)
                    encrypt_data = data[0:ret_fs.cryptor["chunk_size"]]
                    decrypt_data = encrypting.decrypt_content(data_encrypt=encrypt_data,
                                                              chunk_size=ret_fs.cryptor["chunk_size"],
                                                              rota=ret_fs.cryptor['rotate'],
                                                              first_data=ret_fs.cryptor['first-data']
                                                              )
                    ret_data = next(decrypt_data)+data[ret_fs.cryptor["chunk_size"]:]
                    return ret_data
                else:
                    if not hasattr(ret_fs, "buffer_cache"):
                        ret_fs.seek(0)
                        encrypt_data = old_read(ret_fs.cryptor["chunk_size"])
                        ret_fs.seek(pos)
                        decrypt_data = encrypting.decrypt_content(data_encrypt=encrypt_data,
                                                                  chunk_size=ret_fs.cryptor["chunk_size"],
                                                                  rota=ret_fs.cryptor['rotate'],
                                                                  first_data=ret_fs.cryptor['first-data']
                                                                  )
                        setattr(ret_fs, "buffer_cache", next(decrypt_data))
                    if pos+args[0]<=ret_fs.cryptor["chunk_size"]:
                        ret_fs.seek(pos+args[0])
                        return ret_fs.buffer_cache[pos:pos+args[0]]
                    else:
                        # ret_fs.seek(ret_fs.cryptor["chunk_size"])
                        n= args[0]+ pos-ret_fs.cryptor["chunk_size"]
                        ret_fs.seek(ret_fs.cryptor["chunk_size"])
                        next_data = old_read(n)
                        ret_data = ret_fs.buffer_cache[pos:]+ next_data
                        return ret_data
            else:
                data = old_read(*args, **kwargs)
                return data
        else:
            data = old_read(*args, **kwargs)
            ret_data = encrypting.decrypt_content(data_encrypt= data,
                                                  chunk_size=ret_fs.cryptor["chunk_size"],
                                                  rota=ret_fs.cryptor['rotate'],
                                                  first_data=ret_fs.cryptor['first-data'])
            try:
                fx = next(ret_data)
                ret = fx
                while fx:

                    try:
                        fx = next(ret_data)
                        ret += fx
                    except StopIteration:
                        try:
                            return ret.decode("utf-8")
                        except:
                            return ret

                return ret.decode("utf-8")
            except StopIteration:
                return  bytes([])

    setattr(ret_fs, "read", on_read)

    # 1622 /0.472

    return ret_fs
