import sys
text_file = f"/home/vmadmin/python/cy-py/a-working/files/qtsc2.txt"
with open(text_file,"w") as fs:
    fs.write("\nĐây là nội dung khoi tao")
with open(text_file,"rb+") as fs:
    fs.seek(0, 2)  # Seek to the end and obtain current file size
    fs.seek(-1, 2)
    fs.write("O".encode())
with open(text_file,"r") as fs:
    print(fs.read())
sys.path.append("/home/vmadmin/python/cy-py")

import os.path

from cyx.common import config
import cy_file_cryptor

text_file_encrypt = os.path.join(config.file_storage_path, "__gemini_tmp__", "qtsc2.txt")
content =""
with open(text_file,"r") as f:
    content = f.read()
with open(text_file_encrypt,"w") as fs:
    fs.write("\nĐây là nội dung khoi tao")
with open(text_file_encrypt,"a") as fs:
    fs.write("\nĐây là nội dung ghi thêm")
with open(text_file_encrypt,"at") as fs:
    fs.writelines(["\nĐây là nội dung ghi thêm  bang writelines"])

with open(text_file_encrypt,"r",encrypt=True,chunk_size_in_kb=1) as fs:
    content_in_crypt_file = fs.read()
    print(content_in_crypt_file)