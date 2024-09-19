from vn_word_analyzer import analyzer_words, vn_spell,__clear__ , generate_variants
from cyx.ext_libs.vn_predicts import predict_accents
print(predict_accents("tieng viet khong dau"))
txt="trườngkinhtếhinhthứcLÝKHUNGKINHXYZ"
txt="CNXHratxauxa"
txt="tpHCMngay12thang8nam2017"
txt="tpHCMngy12thng8nm2017dahoantattgtinchua?"
txt="oichaokhothemaconlamduoc"
txt="ngay...thang...nam..."
txt="khong"
# fx= analyzer_words("nm2017")[0]
fx,_ = analyzer_words(txt)
for x in generate_variants(txt, True):
    print(x)
