import gc
import typing
from cy_vn_suggestion import utils
from cy_vn_suggestion.analyzers import (
    generate_variants,
    analyzer_words,
    __reverse_tone__
)
from cy_vn_suggestion.generators import (
    covert_to_suggestion_ele,
    generate_suggestions, SuggestionElement
)
from cy_vn_suggestion.gram_calculators import calculator_matrix
from cy_vn_suggestion.settings import __tones__
import phunspell
vn_spell = phunspell.Phunspell("vi_VN")
def suggest(words: str,
            skip_if_in_langs: typing.Optional[typing.List[str]] = ["en_US"],
            correct_spell: bool = True,
            separate_sticky_words: bool = False):
    if words is None: return ""
    if words == "": return ""
    mat, lens_mat = generate_suggestions(words,
                                         detect_langs=skip_if_in_langs,
                                         correct_spell=correct_spell,
                                         separate_sticky_words=separate_sticky_words)
    ret_mat = calculator_matrix(mat, lens_mat)
    ret = ""

    for x in ret_mat:
        ret += " " + x.OW
    del mat
    del lens_mat
    gc.collect()
    return ret.lstrip(' ')


from phunspell import Phunspell

vn_spell = Phunspell("vi_VN")
en_spell = Phunspell("en_US")

def generate_from_vn_spell(words):
    def __compare_word__(a, b):
        from cy_vn_suggestion.analyzers import __reverse_tone__
        if len(a) != len(b): return False
        if len(a) == 2 and len(b) == 2:
            fa = __reverse_tone__.get(a[1].lower())
            fb = __reverse_tone__.get(b[1].lower())
            return fa and fb and fa == fb and a[0].lower() == b[0].lower()

        return True

    ret = []
    ret_lens = []
    word_items = words.split(" ")

    for x in word_items:
        lst = []
        len_x = len(x)
        if len_x == 1:
            tone = __tones__.get(x)
            if tone:
                lst = [SuggestionElement(w) for w in tone]
            else:
                lst = [SuggestionElement(x)]
        elif len_x <=4  and not vn_spell.lookup(x):
            lst = [SuggestionElement(w) for w in vn_spell.suggest(x) if __compare_word__(x, w)]
            if vn_spell.lookup(x):
                lst += [SuggestionElement(x)]
        # elif len_x>=8 and not en_spell.lookup(x):
        elif not en_spell.lookup(x):
            sub_list,sub_lens = generate_suggestions(x,separate_sticky_words=True)
            for sl in sub_list:
                ret+=[sl]
                ret_lens+=[len(sl)]
        lst += [SuggestionElement(x)]
        ret += [lst]
        ret_lens += [len(lst)]
    return ret, ret_lens


def correct_word(words: str):
    if words is None: return ""
    if words == "": return ""
    mat, lens_mat = generate_from_vn_spell(words)
    ret_mat = calculator_matrix(mat, lens_mat)
    ret = ""

    for x in ret_mat:
        ret += " " + x.OW
    del mat
    return ret
