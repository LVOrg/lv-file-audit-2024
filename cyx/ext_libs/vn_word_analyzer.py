import  phunspell
from cyx.ext_libs.vn_predicts import get_config, predict_accents
import cyx.ext_libs.vn_predicts
vn_spell = phunspell.Phunspell("vi_VN")
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


class WordAnalyzer:
    original_word: str
    word: typing.Optional[str]
    left: typing.Optional[str]
    right: typing.Optional[str]
    seek_right:typing.Optional[str]
    vowel: typing.Optional[str]
    provision_word: typing.Optional[str]
    start_of_vowel: int
    end_of_vowel: int

    def __init__(self, word: str):
        self.original_word = word
        self.analyzer_word = word.lower()
        self.left = None
        self.right = None
        self.vowel = None
        self.start_of_vowel = -1
        self.end_of_vowel = -1

    def __create_detect_word__(self):
        if self.right == '':
            self.provision_word = self.left+ self.vowel
            self.seek_right = ""

            return
        if self.right[0] in __full_accents__:
            self.provision_word = self.left+self.vowel
            self.seek_right = ""

            return
        len_of_right = len(self.right)
        for i in range(0,len_of_right):
            if self.right[i] in __full_accents__:

                for k in range(i,len_of_right):
                    if self.right[k] in __full_accents__ :
                        break
                self.seek_right = self.right[0:k]+"*"

                self.provision_word = self.left+self.vowel+self.seek_right
                return

        self.provision_word = self.original_word
        self.seek_right = self.right+"*"



    def get_vn_suggest_words(self):
        len_of_right = len(self.seek_right)
        len_of_left = len(self.left)
        w =""
        ret =[]
        _m=-1
        if self.provision_word=="nhtet":
            print(self)

        for i in range(0,len_of_left):


            for j in range(0,len_of_right):
                w = self.left[i:len_of_left]+self.vowel+self.seek_right[:j]

                lst = [x for x in vn_spell.suggest(w) if __clear__(x)==w]

                if _m<len(w) and len(lst)>0:
                    ret = lst
                    _m = len(w)


        # tmp = word_analyzer(ret[0],skip_provistion=True)

        if self.provision_word[-1]=='*':
            self.provision_word = self.provision_word[:-1]
        index_of_remain = len(self.provision_word) - len(self.left) - len(ret[0])+2
        if ret[0][-1] in __full_accents__:
            index_of_remain-=1

        return ret,self.provision_word[-index_of_remain:]







def word_analyzer(unknown_word: str,skip_provistion=False) -> WordAnalyzer:
    count = 0
    index = 0
    last_vowel_index = 0
    start_vowel_index = None
    ret = WordAnalyzer(unknown_word)
    ret.original_word = unknown_word
    len_of_words = len(unknown_word)
    for i in range(0,len_of_words):
        x = unknown_word[i]
        if x in __full_accents__:
            if start_vowel_index is None:
                start_vowel_index = i
            count += 1
            last_vowel_index = i
            if i<len_of_words-1 and unknown_word[i+1]==x:
                break
            elif i+1< len_of_words and  not unknown_word[i+1] in __full_accents__ and count>0:
                break

        if count == 3:

            ret.start_of_vowel = start_vowel_index - 1
            ret.end_of_vowel_of_vowel = last_vowel_index - 1
            ret.vowel = unknown_word[start_vowel_index - 1:last_vowel_index]
            ret.left = unknown_word[0:start_vowel_index - 1]
            ret.right = unknown_word[last_vowel_index:]
            if not skip_provistion:
                ret.__create_detect_word__()
            return ret
    if count >0:
        ret.start_of_vowel = start_vowel_index
        ret.end_of_vowel_of_vowel = last_vowel_index
        ret.vowel = unknown_word[start_vowel_index:last_vowel_index+1]
        ret.left = unknown_word[0:start_vowel_index]
        ret.right = unknown_word[last_vowel_index+1:]
        if not skip_provistion:
            ret.__create_detect_word__()
        return ret

    return None

def sentence_analyzer(unknown_sentence: str)->typing.List[WordAnalyzer]:
    get_config()
    ret = []
    analyzer = word_analyzer(unknown_sentence)

    while analyzer is not None:
        ret += [analyzer]
        analyzer = word_analyzer(analyzer.right)


    return ret