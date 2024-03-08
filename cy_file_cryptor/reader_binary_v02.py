def do_read(fs, *args, **kwargs):
    from cy_file_cryptor import encrypting
    pos = fs.tell()
    fs.cryptor['header']=fs.cryptor.get('header') or bytes([])
    fs.cryptor['footer'] = fs.cryptor.get('footer') or bytes([])
    header_len = len(fs.cryptor['header'])
    footer_len = len(fs.cryptor['footer'])
    file_size = fs.cryptor["file-size"]
    if len(args)==0:
        if pos ==0:
            """
            Read all data from the first
            """
            ret_data = fs.original_read(*args, **kwargs)

            if footer_len>0:
                return fs.cryptor['header']+ret_data[header_len:-footer_len]+fs.cryptor['footer']
            else:
                return fs.cryptor['header'] + ret_data[header_len:]
        else:
            """
            read all data from position
            """
            if pos<header_len:
                """
                if pos less than  header_len
                return data in header
                """
                return fs.cryptor['header'][:pos]
            elif pos < file_size-footer_len:
                """
                is still being original data
                """
                ret_data = fs.original_read(*args, **kwargs)
                return fs.cryptor['header'][pos:]+ret_data[header_len:-footer_len]+fs.cryptor['footer']
            else:
                return fs.cryptor['footer'][pos:]
    else:
        read_size = args[0]
        if pos+read_size< header_len:
            """
            data will read be in header
            """
            fs.seek(pos+read_size)
            return fs.cryptor['header'][pos:pos+read_size]
        elif pos+read_size < file_size-footer_len:
            ret_data = fs.original_read(*args, **kwargs)
            ret = fs.cryptor['header'][pos:]
            ret+= ret_data[len(ret):]
            return ret

        else:
            ret_data = fs.original_read(*args, **kwargs)
            if ret_data:
                limit = file_size-footer_len-pos
                limit2 = file_size - pos - limit
                return ret_data[:limit] + fs.cryptor['footer'][:limit2]
            else:
                return ret_data


