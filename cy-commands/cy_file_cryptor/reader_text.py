import numpy as np
def do_read(fs, *args, **kwargs):
    # from cy_file_cryptor import encrypting
    data = fs.original_read(*args, **kwargs)
    np_data =np.frombuffer(data, dtype=np.uint8)
    np_data =~np_data
    data_bytes = np_data.tobytes()
    try:
        return data_bytes.decode('utf8')
    except:
        return data_bytes
    # ret_data = encrypting.decrypt_content(data_encrypt=data,
    #                                       chunk_size=fs.cryptor["chunk_size"],
    #                                       rota=fs.cryptor['rotate'],
    #                                       first_data=fs.cryptor['first-data'])
    # try:
    #     fx = next(ret_data)
    #     ret = fx
    #     while fx:
    #
    #         try:
    #             fx = next(ret_data)
    #             ret += fx
    #         except StopIteration:
    #             try:
    #                 return ret.decode("utf-8")
    #             except:
    #                 return (bytes([fs.cryptor["first-data"]])+ret[1:]).decode('utf-8')
    #
    #     return ret.decode("utf-8")
    # except StopIteration:
    #     return bytes([])