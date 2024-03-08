import os
import cy_file_cryptor
import tqdm
file_image = f"/home/vmadmin/python/cy-py/a-working/files/3.png"
from cyx.common import config

file_test = os.path.join(config.file_storage_path, "__gemini_tmp__", "3.png")
file_test_full_block = os.path.join(config.file_storage_path, "__gemini_tmp__", "4-full-block.png")
file_test_full_block_decode = os.path.join(config.file_storage_path, "__gemini_tmp__", "4-full-block-decode.png")
file_test_original = os.path.join(config.file_storage_path, "__gemini_tmp__", "3-org.png")
file_test_original_2 = os.path.join(config.file_storage_path, "__gemini_tmp__", "3-org-3.png")
file_content = None
if os.path.isfile(file_test):
    os.remove(file_test)
fecth_count = 0
n = 1
read_size=0

# with open(file_image, "rb") as f:
#     with open(file_test_full_block,"wb", encrypt=True, chunk_size_in_kb=1) as fs:
#         fs.write(f.read())
# with open(file_test_full_block,"rb", encrypt=True, chunk_size_in_kb=1) as fs:
#     with open(file_test_full_block_decode,"wb") as f:
#         f.write(fs.read())
# h1 = cy_file_cryptor.hash_file(file_image)
# h2 = cy_file_cryptor.hash_file(file_test_full_block_decode)
with open(file_image, "rb") as f:
    file_content = f.read(n)
    while file_content:
        if not os.path.isfile(file_test):
            with open(file_test, "wb", encrypt=True, chunk_size_in_kb=1) as e_file:
                e_file.write(file_content)
        else:
            with open(file_test, "ab", encrypt=True, chunk_size_in_kb=1) as e_file:
                e_file.write(file_content)

        read_size += len(file_content)
        print(f"{os.path.getsize(file_test)}  {read_size}" )

        n= 2*n+1
        file_content = f.read(n)
        print(f"{fecth_count}/{os.path.getsize(file_test)}")
        fecth_count+=n


file_test_original = os.path.join(config.file_storage_path,"__gemini_tmp__","3-org.png")
with open(file_test,"rb")  as e_file:
    data1 = e_file.read()
    with open(file_test_original,"wb")  as fs:
        fs.write(data1)

from PIL import Image
image = Image.open(file_test)
print(f"PIL can read encrypt file {file_test}")