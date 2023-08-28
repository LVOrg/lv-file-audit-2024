from cy_vn_suggestion.loader import get_config
from cy_vn_suggestion.analyzers import analyzer_words, generate_variants
import numpy
import phunspell


class SuggestionElement:
    word: str
    quality: float

    def __init__(self, word: str):
        self.word = word
        self.quality = 0
    def __repr__(self):

        return f"{self.word},{'{:.2f}'.format(self.quality)}"


def covert_to_suggestion_ele(lst):
    ret = []
    for x in lst:
        for v in x:
            ret += [SuggestionElement(x)]
    return numpy.array(ret)


def generate_suggestions(txt: str):
    config = get_config()
    words = txt.split(" ")
    ret = []
    for x in words:
        if config.grams_1.get(x):
            _,pre_fix, vowel,end_fix,_,_ = analyzer_words(x)[0][0]
            end_fix = end_fix or ""
            vowels = config.tones.get(vowel,[])
            sub_list = [SuggestionElement(x)]
            for v in vowels:
                sub_list+= [SuggestionElement(pre_fix+v+end_fix)]
            ret+= [sub_list]
        else:

            for w in generate_variants(x):
                for fw in w:
                    sub_list+=[SuggestionElement(fw)]
                ret += [sub_list]
    ret_mat = numpy.array(ret)
    return ret_mat

