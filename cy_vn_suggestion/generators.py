import typing

from cy_vn_suggestion.loader import get_config
from cy_vn_suggestion.analyzers import (analyzer_words,
                                        generate_variants, check_is_word,
                                        generate_variants_from_analyzer_list
                                        )
from cy_vn_suggestion.utils import (check_is_word,
                                    is_in_langs,
                                    vn_spell)
import numpy


class SuggestionElement:
    W: str
    Q: float
    trace: int

    def __init__(self, word: str):
        self.W = word.lower()
        self.OW = word
        self.Q = 0.0
        self.trace = 0

    def __repr__(self):
        return f"({self.OW},{'{:.2f}'.format(self.Q)},{'{:.2f}'.format(self.trace)})"


def covert_to_suggestion_ele(lst):
    ret = []
    for x in lst:
        for v in x:
            ret += [SuggestionElement(x)]
    return numpy.array(ret)


def __gen__(pre_fix, vowel, end_fix):
    config = get_config()
    vowels = config.tones.get(vowel, [])
    sub_list = []
    if vowels == []:
        return [SuggestionElement(pre_fix + vowel + (end_fix or ""))]
    for v in vowels:
        check_word = pre_fix + v + (end_fix or "")
        l_check_word = check_word.lower()
        if check_is_word(l_check_word):
            sub_list += [SuggestionElement(check_word)]
    if pre_fix != "" and pre_fix[0] == 'd':
        sub_list += __gen__('đ' + pre_fix[1:], vowel, end_fix)
    if pre_fix != "" and pre_fix[0] == 'D':
        sub_list += __gen__('Đ' + pre_fix[1:], vowel, end_fix)
    return sub_list

def generate_probably_word(word:str)->typing.List[str]:
    ret = []
    _, pre_fix, vowel, end_fix, _, _ = analyzer_words(word)[0][0]
    return __gen__(pre_fix, vowel, end_fix)





def generate_suggestions(txt: str, detect_langs: typing.Optional[typing.List[str]]=None):
    try:
        words = txt.split(" ")

        ret = []
        ret_len = []
        cols = -1
        index_of_word = 0
        for x in words:
            lx = x.lower()
            if is_in_langs(x, detect_langs):
                ret += [[SuggestionElement(x)]]
                ret_len += [1]
            else:
                analyzer_list = analyzer_words(lx)[0]
                if analyzer_list is None:
                    sub_list = [SuggestionElement(suggest_word) for suggest_word in vn_spell.suggest(x)]
                    if sub_list.__len__() > 0:
                        ret += [sub_list]
                        ret_len += [len(sub_list)]
                elif analyzer_list.__len__() == 1:
                    sub_list = []
                    _, pre_fix, vowel, end_fix, _, _ = analyzer_list[0]
                    end_fix = end_fix or ""
                    sub_list = __gen__(pre_fix, vowel, end_fix)
                    if sub_list.__len__() > 0:
                        ret += [sub_list]
                        ret_len += [len(sub_list)]
                        if cols < len(sub_list):
                            cols = len(sub_list)
                    else:
                        pre_suggest_word = pre_fix + vowel + end_fix
                        pre_sub_list = [suggest_word for suggest_word in vn_spell.suggest(pre_suggest_word)]
                        if pre_sub_list.__len__() > 0:
                            sub_list = []
                            for wd in pre_sub_list:

                                pre_analyzer_list = analyzer_words(wd)[0]
                                if pre_analyzer_list.__len__() == 1:
                                    _, pre_first, pre_vowel, pre_end, _, _ = pre_analyzer_list[0]
                                    sub_list += __gen__(pre_first, pre_vowel, pre_end)

                            ret += [sub_list]
                            ret_len += [len(sub_list)]
                            if cols < len(sub_list):
                                cols = len(sub_list)
                        else:
                            ret += [pre_suggest_word]
                            ret_len += [1]

                else:
                    has_found = False
                    for suggest_words in generate_variants_from_analyzer_list(analyzer_list):
                        has_found = True
                        sub_list = [SuggestionElement(suggest_word) for suggest_word in suggest_words]
                        if sub_list.__len__() > 0:
                            ret += [sub_list]
                            ret_len += [len(sub_list)]
                    if not has_found:
                        sub_list = [SuggestionElement(suggest_word) for suggest_word in vn_spell.suggest(x)]
                        if sub_list.__len__() > 0:
                            ret += [sub_list]
                            ret_len += [len(sub_list)]
                        else:
                            ret += [[SuggestionElement(x)]]
                            ret_len += [1]

        return ret, ret_len
    except Exception:
        return txt
