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

__clear_map__ = {}
__reverse_tone__ = {}
__reverse_tone__ = {k: k for k, v in __tones__.items()}
__reverse_tone__.update({x: v for k, v in __tones__.items() for x in v})

def __clear__(w):
    clear_map = {'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ụ': 'U', 'Ũ': 'U', 'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U',
                 'Ử': 'U', 'Ự': 'U', 'Ữ': 'U', 'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẹ': 'e', 'ẽ': 'e',
                 'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ệ': 'e', 'ễ': 'e', 'ò': 'o', 'ó': 'o',
                 'ỏ': 'o', 'ọ': 'o', 'õ': 'o', 'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ộ': 'o',
                 'ỗ': 'o', 'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ợ': 'o', 'ỡ': 'o', 'Ò': 'O',
                 'Ó': 'O', 'Ỏ': 'O', 'Ọ': 'O', 'Õ': 'O', 'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O',
                 'Ộ': 'O', 'Ỗ': 'O', 'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ợ': 'O', 'Ỡ': 'O',
                 'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ụ': 'u', 'ũ': 'u', 'ư': 'u', 'ừ': 'u', 'ứ': 'u',
                 'ử': 'u', 'ự': 'u', 'ữ': 'u', 'à': 'a', 'á': 'a', 'ả': 'a', 'ạ': 'a', 'ã': 'a',
                 'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ậ': 'a', 'ẫ': 'a', 'ă': 'a', 'ằ': 'a',
                 'ắ': 'a', 'ẳ': 'a', 'ặ': 'a', 'ẵ': 'a', 'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ạ': 'A',
                 'Ã': 'A', 'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ậ': 'A', 'Ẫ': 'A', 'Ă': 'A',
                 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ặ': 'A', 'Ẵ': 'A', 'ì': 'i', 'í': 'i', 'ỉ': 'i',
                 'ị': 'i', 'ĩ': 'i', 'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẹ': 'E', 'Ẽ': 'E', 'Ê': 'E',
                 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ệ': 'E', 'Ễ': 'E', 'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y',
                 'Ỵ': 'Y', 'Ỹ': 'Y', 'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ị': 'I', 'Ĩ': 'I', 'ỳ': 'y',
                 'ý': 'y', 'ỷ': 'y', 'ỵ': 'y', 'ỹ': 'y'}
    r = ""
    for c in w:
        r+= clear_map.get(c,c)
    return r

import typing

import re
__special_charators__="~!@#$%^&*()_+{}|:\"<>?`1234567890-=[]\\;',./\t\n"
def analyzer_words(text:str,step=0):
    ret =[]
    len_of_text = len(text)
    for i in range(0,len_of_text):
        if text[i] in __special_charators__:
            f=i+1
            while f<len_of_text and text[f] in __special_charators__:f+=1
            if f+1<len_of_text:
                remain = text[f:]
                special=text[i:f]
                next_ret, next_remain = analyzer_words(remain,step+1)
                if step==0:
                    ret += [(text[:i],text[:i],None,None,None,len(text[:i]))]
                ret += [(special, special, None, next_remain, None, len(text[:i]))]
                ret +=next_ret
                return ret,remain
            else:
                return [(text[i:f], text[i:f], None, None, None, len(text[i:f]))],text[0:i]
        j=3
        while j>0:
            if i+j<=len_of_text:
                vowel = text[i:i+j]
                if __reverse_tone__.get(vowel.lower()):
                    remain = text[i+j:]

                    next_ret, next_remain = analyzer_words(remain,step+1)
                    ret += [(text[0:i]+ vowel+ (next_remain or ""),text[0:i], vowel, next_remain,i,len(next_remain or ""))]
                    if next_ret is not None:

                        ret+= next_ret



                    return ret,text[0:i]

            j-=1
    if text !="":
        return None,text
    return None,None





