import os.path
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())

import py_vncorenlp
dir_path ="/data-check/vncorenlp/components"
if not os.path.isdir(dir_path):
    raise Exception(f"{dir_path} was not found")
vn =py_vncorenlp.VnCoreNLP(
        annotators=["wseg"],
        save_dir=dir_path
)
txt= vn.word_segment("Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:")
print(txt)
print("check ok")
