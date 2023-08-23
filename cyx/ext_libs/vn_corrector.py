import typing
# from cyx.ext_libs.vn_predicts import get_config, __config__, __get_gram_count__, predict_accents
import cyx.ext_libs.vn_predicts
import phunspell
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
__check__ = "qwertyuiopasdfghjklzxcvbnmđ"
__chars_end_of_vn_word__ =[
    "t","","p","ng","nh","c","n","m","ch"
]
__chars_begin_of_vn_word__ =[
    "q","e","r","t","","p","s","d","đ","g","h","k","l","x","c",'v','b','n','m',
    "tr","th","ph","gh","kh","ng","nh","ch"
]
vn_pell = phunspell.Phunspell('vi_VN')

def is_vn_word(word:str):


    if word == "mthuyd":
        fx = 1

    if len(word)<=1: return False
    if word[0] in 'zZxXwW': return False
    if word[-1] in 'zZxXwWdD': return False


    index = 0
    pre_index_of_vowel = -1
    last_index_of_vowel=-1
    for x in word:

        if x in __full_accents__:
            last_index_of_vowel= index
            if index>-1 and word[index-1]==x:
                return False
            if  pre_index_of_vowel>-1 and index-pre_index_of_vowel>1:
                return False
            if pre_index_of_vowel==-1:
                pre_index_of_vowel = index
        else:
            if x not in __check__:
                return False
        index +=1
    if pre_index_of_vowel>-1:
        if pre_index_of_vowel==last_index_of_vowel==len(word)-1: return True
        pre_chk =  word[0:pre_index_of_vowel]
        if last_index_of_vowel>-1:

            if word[last_index_of_vowel+1:] in __chars_end_of_vn_word__:
                # if len(word) - 1 == pre_index_of_vowel:
                #     pre_chk = word[0:pre_index_of_vowel]
                # else:
                #     pre_chk = word[0:pre_index_of_vowel - 1]
                if pre_chk in __chars_begin_of_vn_word__:
                    return True

    return False
def suggest_word(word:str):
    if vn_pell.lookup(word):
        return [word]
    ret = []
    len_of_word = len(word)
    lst = vn_pell.suggest(word)
    w1, s1, e1, v1, l1 = sticky_words_analyzer(word)[0]
    for x in lst:
        if len(x)==len_of_word:
            w,s,e,v,l = sticky_words_analyzer(x)[0]


def separated_words(sticky_words:str):
    if sticky_words is None:
        return  []

    words = sticky_words.lower()
    len_of_word = len(words)
    if len_of_word<=2:
        return [sticky_words]
    first_index_of_vowel = -1
    next_index_of_vowel = -1
    ret = []
    next_words = None
    for i in range(0,len_of_word):
        if words[i] in __full_accents__:
            if first_index_of_vowel==-1: first_index_of_vowel = i
            next_index_of_vowel =i
            if i+3<len_of_word and words[i+1:i+3] in __chars_end_of_vn_word__:
                ret = [sticky_words[0:i+3]]
                next_words = sticky_words[i+3:]

            elif i+2<len_of_word and words[i+1:i+2] in __chars_end_of_vn_word__:
                ret = [sticky_words[0:i+2]]
                next_words = sticky_words[i + 2:]
            elif first_index_of_vowel>-1 and first_index_of_vowel+1<len_of_word \
                    and words[first_index_of_vowel+1] in __full_accents__ \
                    and words[first_index_of_vowel+2] in __full_accents__ :
                ret=[sticky_words[0:first_index_of_vowel+2]]
                next_words = sticky_words[first_index_of_vowel+2:]
            elif first_index_of_vowel>-1 and first_index_of_vowel+1<len_of_word and words[first_index_of_vowel+1] not in __full_accents__:
                ret=[sticky_words[0:first_index_of_vowel+1]]
                next_words = sticky_words[first_index_of_vowel+1:]
            if next_words:

                if not vn_pell.lookup(ret[0]):
                    suggest = vn_pell.suggest(ret[0])
                    candidate_word = None
                    for x in suggest:
                        if candidate_word is None:
                            candidate_word =x
                        elif len(candidate_word)<len(x):
                            candidate_word = x
                    ret = [candidate_word]
                    if candidate_word is not None:
                        next_words = words[candidate_word.__len__():]
                        next_ret = separated_words(next_words)
                        ret += next_ret
                        del suggest
                        break
                    else:
                        raise Exception("fail")
                else:
                    next_ret = separated_words(next_words)
                    ret += next_ret
                break
    if len(ret)==0 and first_index_of_vowel>-1 and next_index_of_vowel>-1 and next_index_of_vowel==first_index_of_vowel+1:
        ret=[words[0:next_index_of_vowel+1],words[next_index_of_vowel+1:]]
    return ret




def __split_if_double_vowel__(vowel):
    index = 0
    len_of_vowel = len(vowel)
    for x in vowel:
        if x in __full_accents__:
            if index>0:
                if x==vowel[index-1]:
                    for i in range(index+1,len_of_vowel):
                        if vowel[i] in __full_accents__:
                            return index,i
                    return index,len_of_vowel
        index+=1
    return None,None

def sticky_words_analyzer_clear_double_vowel(data_words):
    global __config__
    ret =[]
    for w,s,e,v,l in data_words:
        s1,e1 = __split_if_double_vowel__(v)
        if s1:
            w1=w[0:s+s1]
            w1_l = len(w1)
            w2=w[s+s1:]
            w2_l = len(w2)
            ret+=[(w1,s1+1,w1_l-1,w1[s:],w1_l)]
            ret += [(w2, 0, e1-s1, w2[0:e1-1],w2_l)]
        else:
            ret+=[(w,s,e,v,l)]
    return ret

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
    for x in unknown_word:

        index += 1

        if x in __full_accents__:
            if start_acc_index is None:
                start_acc_index = index

            if index_acc == index - 1:
                start_next = index
            else:
                count += 1
            if count < 2:
                w += x
                last_acc_index = index
            index_acc = index

        else:
            w += x
        if count == 2:
            nw = unknown_word[last_acc_index:]
            ret += [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index],len(w))]
            ret_next = sticky_words_analyzer(nw) or [(nw, -1, -1, None,len(nw))]
            ret += ret_next
            start_acc_index = None
            return ret
    return [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index],len(w))]

import math
# def __get_log__(old_word,new_word,p_n= None):
#
#     get_config()
#     global  __config__
#     if old_word is None:
#         ret = __config__.grams_1.get(new_word.lower())
#         if ret:
#             ret = (math.log(ret)*-1) **len(new_word)
#         return ret
#     if not  __config__.grams_1.get(new_word.lower()):
#         return  -10000.0
#
#     ret = __config__.grams_2.get((old_word + " " + new_word).lower())
#     if ret:
#         ret= (math.log(ret)*-1) **len(new_word)
#     else:
#         suggest_word = predict_accents((old_word + " " + new_word).lower())
#         ret = __config__.grams_2.get(suggest_word)
#         if ret:
#             ret = (math.log(ret)*-1) **len(new_word)
#         else:
#             ret = -100000.0
#     return ret

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

    ret = []
    w= unclear_word

    __max__ = -10000

    for i in range(0, start):
        check_word = w[i:start] + vowel
        if is_vn_word(check_word):
            val = len(check_word)
            if __max__ < val:
                __max__ = val
                ret = [check_word]
        rm = w[end+1:]
        xw = ""
        for c in rm:
            xw += c
            check_word = w[i:start] + vowel + xw
            if not is_vn_word(check_word):
                continue
            val = len(check_word)
            if __max__ < val:
                __max__ = val
                ret = [check_word]


    if len(ret) ==0:
        ret =[w]
    return ret



def sticky_words_suggestion(analy_list: typing.List[typing.Tuple[str, int, int, str]]):
    # get_config()
    # tones = cyx.ext_libs.vn_predicts.__config__.tones
    max = -1
    found_word = None
    ret = dict()
    previous_word = None

    for w, start, end, vowel in analy_list:
        ret[w] = []
        for i in range(0, start):
            for j in range(0, end):
                ch = w[i:start] + vowel + w[end + 1:-j]
                val = __config__.grams_1.get(ch.lower())
                if val:
                    if max < val:
                        max = val
                        ret[w] += [(ch, val)]



    return ret


