import datetime
import os
import sys
sys.path.append(f"/home/vmadmin/python/cy-py")
from cyx.common import config
file_pdf = f"/home/vmadmin/python/cy-py/a-working/files/bandicam.mp4"
# file_pdf =f"/home/vmadmin/python/cy-py/a-working/files/qtsc2.txt"
file_test = os.path.join(config.file_storage_path, "__gemini_tmp__", "bandicam.mp4")
import shutil

# shutil.rmtree(file_test)
os.makedirs(file_test,exist_ok=True)
import numpy as np
i=0
data_file = os.path.join(file_test,f"data{i}")
hash_size = 0b11111111111

with open(file_pdf,"rb")  as fs:
    # fs.seek(1024)
    data = fs.read()
    while data:
        with open(data_file,"wb") as f:

           header = data[0:hash_size]
           footer = data[-hash_size:]
           body = data[hash_size:-hash_size]

           from cy_file_cryptor.encrypting import encrypt_content
           t = datetime.datetime.utcnow()
           # e_data = data[-512*255:]+data[0:512*255]

           uint8_array_header = np.frombuffer(header, dtype=np.uint8)
           uint8_array_header = uint8_array_header<<1
           uint8_array_footer = np.frombuffer(footer, dtype=np.uint8)
           uint8_array_footer = uint8_array_footer << 1
           # Invert all bits using bitwise NOT (logical negation)
           # inverted_array = ~uint8_array

           # Convert the inverted NumPy array back to a byte array
           # inverted_bytes = inverted_array.tobytes()
           # f.write(uint8_array_header.tobytes())
           f.write(body)
           # f.write(uint8_array_footer.tobytes())
           n = (datetime.datetime.utcnow() - t).total_seconds() * 1000
           print(n)

        i+=1
        data_file = os.path.join(file_test, f"data{i}")
        data = fs.read(hash_size)
