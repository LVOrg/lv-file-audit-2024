from vn_word_analyzer import analyzer_words, vn_spell,__clear__ , spell_suggest
txt="trườngkinhtếhinhthứcLÝKHUNGKINHXYZ"
txt="CNXHratxauxa"
txt="tpHCMngay12thang8nam2017"
txt="tpHCMngy12thng8nm2017dahoantattgtinchua?"
txt="oichaokhothemaconlamduoc!"
# fx= analyzer_words("nm2017")[0]
fx,_ = analyzer_words(txt)
for x in spell_suggest(txt,True):
    print(x)
