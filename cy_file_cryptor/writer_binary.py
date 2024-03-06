def do_write(fs,data):
    from cy_file_cryptor.crypt_info import write_dict
    from cy_file_cryptor import encrypting
    ret = 0
    pos = fs.tell()
    chunk_size = fs.cryptor['chunk_size']
    data_size = len(data)
    if data_size>chunk_size:
        if pos == 0:

            fs.cryptor['first-data'] = data[0]
            fs.cryptor['encoding'] = 'binary'
            write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)
            encrypt_bff = encrypting.encrypt_content(
                data_encrypt= data[0:chunk_size],
                chunk_size=chunk_size,
                rota= fs.cryptor['rotate'],
                first_data=data[0])
            ret += fs.original_write(next(encrypt_bff))
            ret += fs.original_write(data[fs.cryptor['chunk_size']:])
        else:
            ret += fs.original_write(data)
        return ret
    else:
        return bytes([])