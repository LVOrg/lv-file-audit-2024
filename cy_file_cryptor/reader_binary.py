def do_read(fs, *args, **kwargs):
    from cy_file_cryptor import encrypting
    pos =fs.tell()
    if pos < fs.cryptor["chunk_size"]:
        if len(args) == 0:
            data = fs.original_read(*args, **kwargs)
            encrypt_data = data[0:fs.cryptor["chunk_size"]]
            decrypt_data = encrypting.decrypt_content(data_encrypt=encrypt_data,
                                                      chunk_size=fs.cryptor["chunk_size"],
                                                      rota=fs.cryptor['rotate'],
                                                      first_data=fs.cryptor['first-data']
                                                      )
            ret_data = next(decrypt_data) + data[fs.cryptor["chunk_size"]:]
            return ret_data
        else:
            if not hasattr(fs, "buffer_cache"):
                fs.seek(0)
                encrypt_data = fs.original_read(fs.cryptor["chunk_size"])
                fs.seek(pos)
                decrypt_data = encrypting.decrypt_content(data_encrypt=encrypt_data,
                                                          chunk_size=fs.cryptor["chunk_size"],
                                                          rota=fs.cryptor['rotate'],
                                                          first_data=fs.cryptor['first-data']
                                                          )
                setattr(fs, "buffer_cache", next(decrypt_data))
            if pos + args[0] <= fs.cryptor["chunk_size"]:
                fs.seek(pos + args[0])
                return fs.buffer_cache[pos:pos + args[0]]
            else:
                # ret_fs.seek(ret_fs.cryptor["chunk_size"])
                n = args[0] + pos - fs.cryptor["chunk_size"]
                fs.seek(fs.cryptor["chunk_size"])
                next_data = fs.original_read(n)
                ret_data = fs.buffer_cache[pos:] + next_data
                return ret_data

    else:
        data = fs.original_read(*args, **kwargs)
        return data
