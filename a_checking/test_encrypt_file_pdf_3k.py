import os

import cy_file_cryptor.wrappers
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache("localhost:11211")
out_put=f"/home/vmadmin/python/cy-py/a_checking/resources/result/test.pdf"
input = f"/home/vmadmin/python/cy-py/a_checking/resources/demo.pdf"
file_size = os.stat(input).st_size
with open(input,"rb") as fs:
    data = fs.read()
    with open(out_put,"wb",encrypt=True,chunk_size_in_kb=1,file_size=file_size) as fx:
        fx.write(data)