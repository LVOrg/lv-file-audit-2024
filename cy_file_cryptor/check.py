import sys

sys.path.append("/home/vmadmin/python/cy-py")

import os.path

from cyx.common import config
import cy_file_cryptor

# test text file
file_content = ""
# with open("/home/vmadmin/python/cy-py/a-working/files/3.png", "rb") as f:
#     file_content = f.read()  # Read the entire file content as a string
#
#
file_test = os.path.join(config.file_storage_path, "__gemini_tmp__", "3.png")

file_test_orgin = os.path.join(config.file_storage_path, "__gemini_tmp__", "3orgin.png")
# with open(file_test, "wb",encrypt=True,chunk_size_in_kb=1) as file:
#     file.write(file_content)

# with open(file_test_orgin, "wb") as file:
#     file.write(file_content)
file_decode = os.path.join(config.file_storage_path, "__gemini_tmp__", "3decode.png")
file_decode2 = os.path.join(config.file_storage_path, "__gemini_tmp__", "2decode.png")
file_test2 =  os.path.join(config.file_storage_path, "__gemini_tmp__", "4.png")
if os.path.isfile(file_decode2):
    os.remove(file_decode2)

with open(file_test, "r") as file:
    data = file.read(16)

    # file.seek(10)

    while len(data) > 0:
        if not os.path.isfile(file_test2):
            with open(file_test2, "ab", encrypt=True, chunk_size_in_kb=1) as f:
                f.write(data)
        with open(file_test2, "ab", encrypt=True, chunk_size_in_kb=1) as f:
            f.write(data)
        data = file.read(128)
# from PIL import Image
# image = Image.open(file_test)
# print("OK")
"""
0/() /home/vmadmin/python/cy-py/a-working/files/3.png
0/(16,) /mnt/files/__gemini_tmp__/3decode.png
0/(8,) /mnt/files/__gemini_tmp__/3decode.png
8/(8,) /mnt/files/__gemini_tmp__/3decode.png
16/(13,) /mnt/files/__gemini_tmp__/3decode.png
29/(4,) /mnt/files/__gemini_tmp__/3decode.png
33/(8,) /mnt/files/__gemini_tmp__/3decode.png
41/(1,) /mnt/files/__gemini_tmp__/3decode.png
42/(4,) /mnt/files/__gemini_tmp__/3decode.png
46/(8,) /mnt/files/__gemini_tmp__/3decode.png
54/(4,) /mnt/files/__gemini_tmp__/3decode.png
58/(4,) /mnt/files/__gemini_tmp__/3decode.png
62/(8,) /mnt/files/__gemini_tmp__/3decode.png
70/(9,) /mnt/files/__gemini_tmp__/3decode.png
79/(4,) /mnt/files/__gemini_tmp__/3decode.png
83/(8,) /mnt/files/__gemini_tmp__/3decode.png
"""
