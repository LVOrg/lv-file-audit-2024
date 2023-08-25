from vn_word_analyzer import analyzer_words, vn_spell,__clear__
txt="trườngkinhtếhinhthứcLÝKHUNGKINHXYZ"
txt="CNXHratxauxa"
txt="tpHCMngay12thang8nam2017"
txt="tpHCMngy12thng8nm2017dahoantattgtinchua?"
# fx= analyzer_words("nm2017")[0]
fx= analyzer_words(txt)[0]
import re
check_word_1 = lambda x, l: len(x) >= l
check_word_2 = lambda a, b: re.match(a,b)
for fw,f,v,n,i,l in fx:

    suggest =[]
    tt = ""
    if i is None:
        suggest+=[fw]
        print(f"{fw}->{suggest}")
        continue

    for ii in range(0,i):
        _pattern_ = f[ii:]+".*"+v
        cw = f[ii:] + v
        len_of_cw = len(cw)
        if len_of_cw>1: suggest+=[x for x in vn_spell.suggest(cw)]

        for k in range(0,l):
            cw+=(n or "")[k]
            if len_of_cw>1: suggest += [x for x in vn_spell.suggest(cw)]
            # if vn_spell.suggest(cw):
            #     suggest += [cw]
            # else:
            # if vn_spell.lookup(cw):
            #     suggest+=[x for x in vn_spell.suggest(cw) if __clear__(x)==__clear__(cw)]


    print(f"{fw}->{suggest}")


