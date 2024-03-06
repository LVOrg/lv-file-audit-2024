import os
import cy_file_cryptor
file_word = f"/home/vmadmin/python/cy-py/a-working/files/bbtt.docx"
from cyx.common import config
file_test = os.path.join(config.file_storage_path,"__gemini_tmp__","bbtt.docx")
file_test_original = os.path.join(config.file_storage_path,"__gemini_tmp__","bbtt-original.docx")
file_content = None
with open(file_word,"rb") as f:
    file_content = f.read()

with open(file_test,"wb",encrypt=True,chunk_size_in_kb=1) as e_file:
    e_file.write(file_content)
with open(file_test,"rb")  as e_file:
    with open(file_test_original,"wb")  as fs:
        fs.write(e_file.read())