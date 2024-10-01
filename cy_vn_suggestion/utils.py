import threading
import typing

from cy_vn_suggestion.loader import get_config
from cy_vn_suggestion.settings import __full_accents__
import phunspell

vn_spell = phunspell.Phunspell("vi_VN")


def check_is_word(word: str):
    # __config__ = get_config()
    # return __config__.grams_1.get(word) and vn_spell.lookup(word)
    return vn_spell.lookup(word)


def get_gram_count(ngram_word, ngrams):
    if ngrams.get(ngram_word) is None:
        return 0
    output = ngrams[ngram_word]
    return output


__langs__detections__ = None
__lock__ = threading.Lock()


def is_in_langs(word: str, lans: typing.Optional[typing.List[str]] = None):
    if lans is None or  len(lans) ==0: return False

    global __langs__detections__
    if __langs__detections__ is None:
        __lock__.acquire()

        try:
            __langs__detections__ = {}
            for x in lans:
                __langs__detections__[x] = phunspell.Phunspell(x)
        except Exception as e:
            __langs__detections__ = None
            raise e
        finally:
            __lock__.release()

    for k, v in __langs__detections__.items():
        if v.lookup(word):
            return True
        else:
            return False

def is_vn_sticky_words(txt:str)->bool:
    """
    MUAVÉXE
    :param txt:
    :return:
    """
    from  cy_vn_suggestion.settings import __full_accents__
    len_of_text = len(txt)
    first_index_of_vowel = 0
    while first_index_of_vowel<len_of_text and txt[first_index_of_vowel] not in __full_accents__:
        first_index_of_vowel+=1
    if first_index_of_vowel==len_of_text:
        return False
    next_index_of_vowel = first_index_of_vowel+1
    while next_index_of_vowel<len_of_text and txt[next_index_of_vowel] in __full_accents__:
        next_index_of_vowel+=1
