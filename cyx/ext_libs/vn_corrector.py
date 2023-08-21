import typing
from cyx.ext_libs.vn_predicts import get_config, __config__
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
            ret += [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index])]
            ret_next = sticky_words_analyzer(nw) or [(nw, -1, -1, None)]
            ret += ret_next
            start_acc_index = None
            return ret
    return [(w, start_acc_index - 1, last_acc_index - 1, w[start_acc_index - 1:last_acc_index])]


def sticky_words_suggestion(analy_list: typing.List[typing.Tuple[str, int, int, str]]):
    get_config()
    tones = cyx.ext_libs.vn_predicts.__config__.tones
    for w,start,end,vowel in analy_list:
        print(f"{vowel} ->  {tones[vowel]}")
