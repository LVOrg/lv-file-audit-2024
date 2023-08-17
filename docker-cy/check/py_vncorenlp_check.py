import pathlib
import sys
sys.path.append("/app")
import re
w = pathlib.Path(__file__).parent.__str__()

from underthesea import word_tokenize
clear_content = "Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:"
ret = word_tokenize(clear_content)
print(ret)
