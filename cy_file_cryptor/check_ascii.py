import os
from cyx.common import config
from cy_file_cryptor.encrypting import decrypt_content,encrypt_content,print_bytes
data= "ky tu dau tien"

file_test = os.path.join(config.file_storage_path,"__gemini_tmp__","test-ascii.txt")
with open(file_test,"wb",encrypt=True,chunk_size_in_kb=4) as f:
    f.write(data)
# with open(file_test,"ab",encrypt=True,chunk_size_in_kb=4) as f:
#     f.write("ky tu thu 2")

with open(file_test,"r") as f:

    data = f.read()



