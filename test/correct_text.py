
# from cyx.ext_libs.vn_predicts import correct_accents,is_accent_word,seperate_words_clear,vn_clear_sticky
from cyx.ext_libs.vn_corrector import sticky_words_analyzer,sticky_words_suggestion
# fx = vn_clear_sticky("trườngkinhtếhinhthứcLÝKHUNGKINHXYZ")
# fx = vn_clear_sticky("cacphuongphapquanlynenkinhteusa")
fx = sticky_words_analyzer("cacphuongphapquanlynenkinhteusa")
sticky_words_suggestion(fx)
print(fx)
fx = sticky_words_analyzer("cacphuongtautantaisansangusa")
print(fx)
"""
hinhth 
thứcL
cLÝKH
KHUNGK
NGKINHXY
Z
"""
# print(fx)
# txt = "Trong đó, hinh thức làm việc:."
# words = txt.split(" ")
# r = [x for x in words if is_accent_word(x)]
# print(r)
# fx= correct_accents(txt)
# print(fx)