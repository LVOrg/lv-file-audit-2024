import typing
from cyx.ext_libs.vn_predicts import get_config, __config__, __get_gram_count__, predict_accents
import cyx.ext_libs.vn_predicts

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


def sticky_words_analyzer(unknown_word: str) -> typing.List[str]:
    """
    analizier
    :param unknown_word:
    :return:
    """
    ret = []
    w = ""
    count = 0
    index_acc = 0
    index = 0
    last_acc_index = 0
    start_acc_index = None
    pre_acc = None

    for x in unknown_word:

        index += 1

        if x in __full_accents__:
            if start_acc_index is None:
                start_acc_index = index
            if index>1:
                pre_acc = unknown_word[index-2]


            if index_acc == index - 1:
                if pre_acc==x:
                    w+=x
                    ret_ = [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index],len(w))]
                    rx = unknown_word[w.__len__():]
                    r_ = sticky_words_analyzer(rx)
                    print(rx)
                else:
                    count += 1





            if count < 2:
                w += x
                last_acc_index = index
            else:
                count += 1
            index_acc = index


        else:
            w += x
        if count == 2:
            nw = unknown_word[last_acc_index:]
            ret += [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index],len(w))]
            ret_next = sticky_words_analyzer(nw) or [(nw, -1, -1, None,len(nw))]
            ret += ret_next
            start_acc_index = None
            pre_acc = None
            return ret
    return [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index],len(w))]

import math
def __get_log__(old_word,new_word,p_n= None):
    if new_word=="thức":
        fx=1
    get_config()
    global  __config__
    if old_word is None:
        ret = __config__.grams_1.get(new_word.lower())
        if ret:
            ret = ret **len(new_word)
        return ret
    if not  __config__.grams_1.get(new_word.lower()):
        return  -10000.0

    ret = __config__.grams_2.get((old_word + " " + new_word).lower())
    if ret:
        ret= ret**len((new_word))
    else:
        suggest_word = predict_accents((old_word + " " + new_word).lower())
        ret = __config__.grams_2.get(suggest_word)
        if ret:
            ret = ret ** len((new_word))
        else:
            ret = -100000.0
    return ret

    # number2Gram = __get_gram_count__(old_word + " " + new_word, __config__.grams_2)**len(new_word)
    # number1Gram = __get_gram_count__(old_word, __config__.grams_1)**len(new_word)
    #
    # if number1Gram > 0 and number2Gram > 0:
    #     log = math.log((number2Gram + 1) / (number1Gram + __config__.statistic[old_word]))
    # else:
    #     log = math.log(1.0 / (2 * (__config__.size_2_grams + __config__.total_count_2_grams)))
    # if p_n:
    #     log += math.log(
    #         (number1Gram + 1) / (__config__.size_1_gram + __config__.total_count_1_gram))
    # return log**(len(new_word))


def sticky_words_get_suggest_list(unclear_word, start, end, vowel,len_of_word,previous_word=None):
    get_config()
    tones = cyx.ext_libs.vn_predicts.__config__.tones
    ret = []
    w= unclear_word
    fw = None
    __max__ = -10000
    tone = tones.get(vowel)
    if previous_word=="tế":
        fx=1
    if w == "nhthứcL":
        fx = 1
    for i in range(0, start):
        for j in range(end+1,len_of_word):

            if not tone:
                ch = w[i:start] + vowel + w[end+1:j]
                if not __config__.grams_1.get(ch.lower()):
                    continue
                val = __get_log__(previous_word, ch)
                if __max__ < val:
                    __max__ = val
                    __max_len__ = len(ch)
                    ret = [ch]

            else:

                ch = w[i:start] + vowel +  w[end+1:j]
                if not __config__.grams_1.get(ch.lower()):
                    continue
                val = __get_log__(previous_word,ch.lower())
                if val:
                    val = val ** len(ch)
                    if __max__ < val:
                        __max__ = val
                        ret = [ch]
                for x in tone:

                    ch = w[i:start] + x +  w[end+1:j]
                    if not __config__.grams_1.get(ch.lower()):
                        continue
                    val = __get_log__(previous_word, ch.lower())
                    if __max__ < val:
                        __max__ = val
                        __max_len__ = len(ch)
                        ret = [ch]




    if len(ret) ==0:
        ret =[w]
    return ret



def sticky_words_suggestion(analy_list: typing.List[typing.Tuple[str, int, int, str]]):
    get_config()
    tones = cyx.ext_libs.vn_predicts.__config__.tones
    max = -1
    found_word = None
    ret = dict()
    previous_word = None

    for w, start, end, vowel in analy_list:
        ret[w] = []
        for i in range(0, start):
            for j in range(0, end):
                tone = tones.get(vowel)
                if not tone:
                    ch = w[i:start] + vowel + w[end + 1:-j]
                    if previous_word:
                        ch_word = previous_word + " " + ch
                        val = __config__.grams_2.get(ch_word.lower())
                        if val:
                            if max < val:
                                max = val
                                ret[w] += [(ch, val)]

                    else:
                        val = __config__.grams_1.get(ch.lower())
                        if val:
                            if max < val:
                                max = val
                                ret[w] += [(ch, val)]

                else:
                    for x in tone:
                        ch = w[i:start] + x + w[end + 1:-j]
                        if previous_word:
                            ch_word = previous_word + " " + ch
                            val = __config__.grams_2.get(ch_word.lower())
                            if val:
                                if max < val:
                                    max = val
                                    ret[w] += [(ch, val)]

                        else:
                            val = __config__.grams_1.get(ch.lower())
                            if val:
                                if max < val:
                                    max = val
                                    ret[w] += [(ch, val)]

        print(f"{vowel} ->  {tones[vowel]}")
