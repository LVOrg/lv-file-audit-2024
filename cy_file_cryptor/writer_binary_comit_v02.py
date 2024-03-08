import os


def do_commit(fs, header_size, footer_size):
    # from cy_file_cryptor import encrypting
    from cy_file_cryptor.crypt_info import write_dict

    # if len(fs.cryptor['footer']) > 0:
    #     fs.seek(-len(fs.cryptor['footer']), 2)
    #     fs.original_write(os.urandom(len(fs.cryptor['footer'])))

    fs.cryptor['encoding'] = 'binary'
    fs.cryptor["file-size"] = fs.file_size
    write_dict(fs.cryptor, fs.cryptor_rel, fs.original_open_file)

    ret = fs.original_close()

    return ret
