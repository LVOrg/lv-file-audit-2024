import pathlib
w = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(w)
import os
import py_vncorenlp
data_path = '/home/vmadmin/python/v6/file-service-02/cyx/rdr_segmenter/vncorenlp/components'
if not os.path.isdir(data_path):
    data_path='/app/cyx/rdr_segmenter/vncorenlp/components'
    if not os.path.isdir(data_path):
        raise Exception(f"{data_path} was not found")
rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"],
                                                   save_dir=data_path)
txt = "Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:"
fx =rdrsegmenter.word_segment(txt)
print(txt)
print(fx)

