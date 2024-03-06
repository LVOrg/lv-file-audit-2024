import sys

sys.path.append("/home/vmadmin/python/cy-py")

import os.path

from cyx.common import config
import cy_file_cryptor

# test text file
file_content = ""
with open("/home/vmadmin/python/cy-py/a-working/files/con-cho.jpg", "rb") as f:
    file_content = f.read()  # Read the entire file content as a string


file_encrypt = os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-encrypt.jpg")
file_encrypt_part = os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-encrypt-part.jpg")
file_encrypt_part_001 = os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-encrypt-part-001.jpg")
file_encrypt_part_002 = os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-encrypt-part-002.jpg")
file_origin = os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-origin.png")
file_origin_part= os.path.join(config.file_storage_path, "__gemini_tmp__", "con-cho-origin-part.png")

with open(file_encrypt,"rb") as f:
    with open(file_encrypt_part_002,mode="wb",encrypt=True,chunk_size_in_kb=3) as fs:
        data = f.read(1024)
        fs.write(data)

    with open(file_encrypt_part_002,"ab") as fs:
        while data:
            data = f.read(512)
            fs.write(data)

# with open(file_encrypt,"wb",encrypt=True,chunk_size_in_kb=1) as e_file:
#     e_file.write(file_content)
#decrypt file
# with open(file_encrypt_part,"rb") as e_file:
#
#     with open(file_origin_part,"wb") as o_file:
#         data = e_file.read(1024 * 3)
#         o_file.write(data)
#
#     while data:
#         with open(file_origin_part, "ab") as o_file:
#             data = e_file.read(512)
#             o_file.write(data)



from PIL import Image
image = Image.open(file_encrypt_part_002)
print("OK")
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
