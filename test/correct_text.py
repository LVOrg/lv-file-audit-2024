
from cyx.ext_libs.vn_predicts import correct_accents,is_accent_word, predict_accents
print(predict_accents("chi chung do thoi la du roi"))
print(predict_accents("tet nay khong can banh tet"))
print(predict_accents("chi bay nhieu da du chua"))
print(predict_accents("chi bay nhieu ly thuyet da du chua"))
print(predict_accents("cha thay do dan gi het"))
print(predict_accents("ly thuyet Ok thuc te sai"))

from cyx.ext_libs.vn_corrector import sticky_words_analyzer,sticky_words_suggestion, sticky_words_get_suggest_list
from cyx.ext_libs.vn_predicts import  predict_accents
# fx = vn_clear_sticky("trườngkinhtếhinhthứcLÝKHUNGKINHXYZ")
# fx = vn_clear_sticky("cacphuongphapquanlynenkinhteusa")
import langdetect
ffx = fx = predict_accents("truong kinh tế hinh thức LÝ HUNG KINH XYZ")
print(ffx)
#fx = sticky_words_analyzer("truongkinhtếhinhthứcLÝKHUNGKINHXYZ")
fx = sticky_words_analyzer("oikhothemaconlamduoc")
# w,start,end,vowel = fx[0]
# ret = sticky_words_get_suggest_list(w,start,end,vowel)
# print(ret)
p_list = None
r =[]
ret= None
pr = None
for w,start,end,vowel,len_of_word in fx:
    if w=="nhtếh":
        fx=1
    ret = sticky_words_get_suggest_list(w,start,end,vowel,len_of_word,pr)
    pr=ret[0]
    r += ret
    print(r)



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