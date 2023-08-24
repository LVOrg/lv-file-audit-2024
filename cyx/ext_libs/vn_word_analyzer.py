import  phunspell
# from cyx.ext_libs.vn_predicts import get_config, predict_accents
# import cyx.ext_libs.vn_predicts
vn_spell = phunspell.Phunspell("vi_VN")
__tones__ = {
     "iay": ["iẩy", "iâý", "iẫy", "iay", "iấy", "iày", "ìay", "iầy", "iáy", "iãy", "iạy", "iây", "iảy"],
     "uy": ["ùy", "uý", "uỹ", "uy", "úy", "ụy", "uỳ", "ũy", "ủy", "uỵ", "uỷ"],
     "oa": ["oâ", "oẳ", "oặ", "oà", "óa", "õa", "oằ", "oẫ", "oã", "ọa", "oắ", "oă", "oả", "oẵ", "òa", "oa", "ỏa", "oạ", "oá"],
     "oi": ["ối", "ỏi", "ốí", "ơỉ", "ộí", "ọi", "ời", "ói", "ớỉ", "ỡi", "ộị", "ọị", "ợị", "ờị", "ổỉ", "ồì", "ởỉ", "ôị", "õi", "ợi", "ôí", "ôì", "ờì", "ơì", "óí", "ôi", "ồi", "òi", "ơí", "ơi", "oi", "ỏỉ", "ỗi", "ơị", "ôỉ", "ôĩ", "ờĩ", "ổi", "ội", "ởi", "ới", "ớí"],
     "a": ["ạ", "ã", "â", "ẳ", "ặ", "a", "ẩ", "ấ", "ă", "ả", "à", "ẵ", "á", "ắ", "ẫ", "ằ", "ầ", "ậ"],
     "ua": ["uậ", "uă", "ưa", "uặ", "uắ", "úa", "ửa", "uẵ", "uẩ", "uá", "ùa", "ứa", "uẫ", "uà", "ũa", "ụa", "uầ", "ủa", "uấ", "uẳ", "uạ", "uả", "uằ", "ừa", "uã", "ựa", "ữa", "uâ", "ua"],
     "o": ["ớ", "ỗ", "ổ", "ơ", "ố", "ò", "õ", "ộ", "ở", "ô", "ợ", "ọ", "ỡ", "ỏ", "o", "ồ", "ó", "ờ"],
     "uu": ["ứu", "ựu", "ưu", "ửu", "ữu", "ừu"],
     "uo": ["ưở", "uỡ", "uớ", "ượ", "ưỡ", "uở", "ươ", "uờ", "uổ", "uỗ", "uô", "ườ", "ướ", "uồ", "uộ", "uợ", "uơ", "uố", "uọ"],
     "eo": ["ểo", "ẽo", "èo", "ẹo", "ẻo", "éo", "eo"],
     "oai": ["oai", "oải", "oàì", "oài", "oái", "oại", "oãi"],
     "yeu": ["yễu", "yêu", "yểu", "yệu", "yếu", "yeu", "yều"],
     "uou": ["ượu", "ươu"],
     "uoi": ["uội", "uôí", "uồi", "uổi", "uối", "ười", "ướí", "ườì", "ưỡi", "ượi", "uoi", "uỗi", "ươi", "ưới", "uôi"],
     "ieu": ["iểu", "iếu", "iệu", "iễu", "iêu", "iều"],
     "uay": ["uậy", "uảy", "uây", "uẩy", "uầy", "uấy", "uay", "uẫy", "uày"],
     "iu": ["iủ", "iụ", "iử", "iứ", "ỉu", "iư", "iừ", "íu", "ìu", "iú", "iữ", "iự", "iu", "ĩu", "iù", "ịu", "iũ"],
     "ia": ["iă", "ĩa", "iấ", "iặ", "iả", "ỉa", "iẳ", "iẵ", "iậ", "iắ", "iâ", "iầ", "iã", "iá", "iạ", "ịa", "ìa", "ià", "ía", "iẩ", "iằ", "iẫ", "ia"],
     "ou": ["ơu", "ớu", "ởu"],
     "ueo": ["ueo", "uẹo", "uéo", "uèo"],
     "ui": ["ừi", "ửi", "ữi", "ùi", "úi", "ũi", "ui", "ủi", "ưi", "ứi", "ựi", "uì", "ụi"],
     "iuo": ["iướ", "iươ", "iưò", "iuố", "iuộ", "iuồ", "iưỡ", "iườ", "iượ", "iưở"],
     "io": ["iỏ", "iồ", "iỡ", "iô", "iợ", "iố", "iộ", "iơ", "iọ", "ío", "io", "iờ", "iớ", "iỗ", "iở", "iò", "iổ", "iõ", "ió"],
     "e": ["ê", "e", "ề", "ế", "é", "ể", "ẹ", "ễ", "è", "ẻ", "ệ", "ẽ"],
     "ao": ["ăo", "ằo", "âo", "ắo", "ao", "ào", "áo", "ão", "ạo", "ậo", "ảo", "ấo"],
     "ue": ["uẻ", "uẹ", "ùe", "uè", "uể", "uế", "ue", "uẽ", "úe", "uề", "uê", "ué", "uễ", "uệ"],
     "iau": ["iàu"],
     "au": ["ãu", "ảu", "ậu", "ẩu", "ạu", "ầu", "àu", "ẫu", "ắu", "ấu", "au", "âu", "áu"],
     "uye": ["ưyễ", "uyê", "uyé", "uyẹ", "ưyê", "uyẻ", "uyế", "uyè", "uye", "uyễ", "uyề", "uyệ", "uyể", "uyẽ"],
     "ai": ["âi", "àì", "ại", "ăi", "ải", "ãi", "ẩi", "ấi", "ái", "ầi", "ài", "ắi", "ai", "ẫi"],
     "oay": ["oay", "oày", "oạy", "oáy", "oảy", "oãy"],
     "ioi": ["iới", "iời", "iỏi"],
     "uya": ["uyã", "ưya", "uyạ", "uyấ", "uya", "uyá", "uyả"],
     "eu": ["ệu", "ều", "êu", "ểu", "ếu"],
     "ay": ["ăy", "áy", "ậy", "ẫy", "ạy", "ảy", "ầy", "ắy", "ây", "ày", "ay", "ấy", "ãy", "ẩy"],
     "iai": ["iai", "iãi", "iại", "iảỉ", "iái", "iài", "iải"],
     "ye": ["yễ", "yẻ", "yề", "yệ", "yế", "yể", "yẽ", "yé", "yê"],
     "ieo": ["iẻo", "ieo"],
     "uao": ["uao", "uáo", "uào", "uạo"],
     "ie": ["iè", "iề", "ỉe", "ịe", "iẽ", "iễ", "ìe", "ĩe", "iẻ", "ie", "iê", "ìệ", "ỉệ", "iế", "iệ", "íe", "ié", "iể"],
     "uau": ["uạu", "uàu"],
     "oe": ["ọe", "oe", "oè", "oẹ", "ỏe", "oẽ", "oế", "óe", "oé", "oẻ", "òe", "õe", "oệ", "oề"],
     "i": ["i", "í", "ị", "ĩ", "ỉ", "ì"],
     "iao": ["iáo", "iao", "iạo", "iảo", "iào"],
     "iua": ["iua", "iữa", "iùa", "iứa", "iừa", "iụa", "iửa", "iựa", "iưa"],
     "y": ["ỷ", "ỵ", "ý", "ỳ", "y", "ỹ"],
     "uyo": ["uyồ", "uyo", "uyộ"],
     "uyu": ["uỷu", "uỵu", "uyu"],
     "uai": ["uãi", "uái", "uải", "uai", "uài", "uại"],
     "iui": ["iụi", "iữi", "iúi", "iùi", "iửi", "iứi", "iũi"],
     "u": ["ừ", "ủ", "ụ", "ữ", "ù", "ử", "ú", "ứ", "ũ", "u", "ư", "ự"],
}
__no__accent_map__ = [f"UÙÚỦỤŨƯỪỨỬỰỮ",
                    f"eèéẻẹẽêềếểệễ",
                    f"oòóỏọõôồốổộỗơờớởợỡ",
                    f"OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ",
                    f"uùúủụũưừứửựữ",
                    f"aàáảạãâầấẩậẫăằắẳặẵ",
                    f"AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ",
                    f"iìíỉịĩ",
                    f"EÈÉẺẸẼÊỀẾỂỆỄ",
                    f"YỲÝỶỴỸ",
                    f"IÌÍỈỊĨ",
                    f"yỳýỷỵỹ"]
__clear_map__ = {}
__reverse_tone__ = {}
for k,v in __tones__.items():
    __reverse_tone__[k]=k
    for x in v:
        __reverse_tone__[x]=v
for x in __no__accent_map__:

    for ii in range(1,len(x)):
        __clear_map__[x[ii]]=x[0]
def __clear__(w):
    r = ""
    for c in w:
        r+= __clear_map__.get(c,c)
    return r
__full_accents__ = (f"UÙÚỦỤŨƯỪỨỬỰỮ"
                    f"eèéẻẹẽêềếểệễ"
                    f"oòóỏọõôồốổộỗơờớởợỡ"
                    f"OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ"
                    f"uùúủụũưừứửựữ"
                    f"aàáảạãâầấẩậẫăằắẳặẵ"
                    f"AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ"
                    f"iìíỉịĩ"
                    f"EÈÉẺẸẼÊỀẾỂỆỄ"
                    f"YỲÝỶỴỸ"
                    f"IÌÍỈỊĨ"
                    f"yỳýỷỵỹ")

import typing

import re
def analyzer_words(text:str):
    ret =[]
    len_of_text = len(text)
    for i in range(0,len_of_text):
        j=3
        while j>0:
            if i+j<=len_of_text:
                vowel = text[i:i+j]
                if __reverse_tone__.get(vowel.lower()):
                    remain = text[i+j:]

                    next_ret, next_remain = analyzer_words(remain)
                    ret += [(text[0:i]+ vowel+ (next_remain or ""),text[0:i], vowel, next_remain,i,len(next_remain or ""))]
                    if next_ret is not None:

                        ret+= next_ret

                    return ret,text[0:i]

            j-=1
    if text !="":
        return None,text
    return None,None





