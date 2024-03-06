import os
from cyx.common import config
from cy_file_cryptor.encrypting import decrypt_content,encrypt_content,print_bytes
data= "2. Ý kiến Lãnh đạo Văn phòng \n"

file_test = os.path.join(config.file_storage_path,"__gemini_tmp__","test-001.txt")
with open(file_test,"a",encrypt=True,chunk_size_in_kb=4) as f:
    for i in range(0,10):
        f.writelines([f"test {i}", data])

with open(file_test,"r") as f:

    data = f.read()
    print(data.decode())


