from vn_word_analyzer import analyzer_words, vn_spell,__clear__
txt="trườngkinhtếhinhthứcLÝKHUNGKINHXYZ"
txt="CNXHratxauxa"
fx= analyzer_words(txt)[0]

for fw,f,v,n,i,l in fx:

    suggest =[]
    tt = ""
    for ii in range(0,i):

        cw = f[ii:] + v
        if vn_spell.lookup(cw):
            suggest+=[cw]
        else:
            suggest+=[x for x in vn_spell.suggest(cw) if __clear__(x)==__clear__(cw)]
        for k in range(0,l):
            cw+=(n or "")[k]
            if vn_spell.suggest(cw):
                suggest += [cw]
            else:
                suggest+=[x for x in vn_spell.suggest(cw) if __clear__(x)==__clear__(cw)]


    print(f"{fw}->{suggest}")


