import sys
sys.path.append("/home/vmadmin/python/cy-py")

import os.path

from cyx.common import config
import cy_file_cryptor
#test text file
file_content=""
with open("/home/vmadmin/python/cy-py/a-working/files/XuLynoiDung.yml", "rb") as f:
    file_content = f.read()  # Read the entire file content as a string


file_test = os.path.join(config.file_storage_path,"__gemini_tmp__","XuLynoiDung.yml")
with open(file_test, "w",encrypt=True,chunk_size_in_kb=10) as file:
    file.write(file_content)