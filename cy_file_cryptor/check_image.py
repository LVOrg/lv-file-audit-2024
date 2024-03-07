import os
import cy_file_cryptor
file_image = f"/home/vmadmin/python/cy-py/a-working/files/3.png"
from cyx.common import config
file_test = os.path.join(config.file_storage_path,"__gemini_tmp__","3.png")
file_test_original = os.path.join(config.file_storage_path,"__gemini_tmp__","3-org.png")
file_content = None
with open(file_image,"rb") as f:
    file_content = f.read()

with open(file_test,"wb",encrypt=True,chunk_size_in_kb=1) as e_file:
    e_file.write(file_content)
if os.path.isfile(file_test_original):
    os.remove(file_test_original)
with open(file_test,"rb")  as e_file:
    data1 = e_file.read(15)
    with open(file_test_original,"wb")  as fs:
        fs.write(data1)

    data1 = e_file.read(15)
    with open(file_test_original, "ab") as fs:
        fs.write(data1)
    data1 = e_file.read(15)
    with open(file_test_original, "ab") as fs:
        fs.write(data1)
    data1 = e_file.read(15)
    with open(file_test_original, "ab") as fs:
        fs.write(data1)
    data1 = e_file.read(15)
    with open(file_test_original, "ab") as fs:
        fs.write(data1)
    data1 = e_file.read(1500)
    while data1:
        with open(file_test_original,"ab")  as fs:
            fs.write(data1)
        data1 = e_file.read(1023)
from PIL import Image
image = Image.open(file_test)
print(f"PIL can read encrypt file {file_test}")