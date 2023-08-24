# from cyx.ext_libs.vn_predicts import get_config, __config__
import collections
import os.path
import pathlib
import phunspell
# vn_check = phunspell.Phunspell("vi_VN")
import cyx.ext_libs.vn_predicts
from json import dumps
from cyx.ext_libs.vn_validator import is_vn_word
from cyx.tools.progress_bar import printProgressBar
cyx.ext_libs.vn_predicts.get_config()
g2 = cyx.ext_libs.vn_predicts.__config__.tones
txt=dumps(g2, ensure_ascii=False).encode("utf-8")
file_name="/home/vmadmin/python/cy-py/cyx/ext_libs/data.txt"
with open(file_name, "w") as f:
    f.write(txt.decode("utf8").replace("],","],\n"))
lines =[]
for k,v in g2.items():
    lines+=[]
    if len(k)==2:
        print(f"'{k}':{list(sorted(v,reverse=True))}")
# gram_1 = collections.OrderedDict()
#
# total = len(g2.keys())
# index = 0
# c=0
# for k,v in g2.items():
#     if ' ' in k:
#         ws = k.split(' ')
#         if vn_check.lookup(ws[0]) and vn_check.lookup(ws[1]):
#             gram_1[k] = v
#             c += 1
#
#     index += 1
#     printProgressBar(
#         iteration=index,
#         length=50,
#         prefix=f"Validate {index}/{c}",
#         total= total,
#
#     )
#
#
# import numpy as np
# location = pathlib.Path(__file__).parent.__str__()
# np.save(os.path.join(
#     location,"vn_predictor_grams2.npy"
# ),gram_1)
# print(f"{c}/{total}")