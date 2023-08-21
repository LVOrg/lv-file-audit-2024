import math
import os
import pathlib
import re
import typing
import numpy
import zipfile
import collections
import numpy as np
import langdetect

__working_dir__ = pathlib.Path(__file__).parent.parent.__str__()


def __load_data_from_zip__(data_zip_file: str, dataset_path: str = None) -> collections.OrderedDict:
    if os.path.splitext(data_zip_file)[1] != ".zip":
        raise Exception(f"{data_zip_file} is not zip file")
    if not os.path.isfile(data_zip_file):
        raise FileNotFoundError(data_zip_file)
    if dataset_path is None:
        dataset_path = os.path.join(
            pathlib.Path(data_zip_file).parent.__str__(),
            "dataset")
    os.makedirs(dataset_path, exist_ok=True)
    numpy_file = os.path.join(
        dataset_path,
        f"{pathlib.Path(data_zip_file).stem}"
    )
    if not os.path.isfile(numpy_file):
        with zipfile.ZipFile(data_zip_file, "r") as zip_ref:
            zip_ref.extractall(dataset_path)
    ret = numpy.load(numpy_file, allow_pickle='TRUE').item()
    return ret


def load_ordered_dict_from_file(file_name):
    """Loads a collections.OrderedDict from a file using numpy.

  Args:
    file_name: The file name to load the collections.OrderedDict from.

  Returns:
    A collections.OrderedDict.
  """

    with open(file_name, "rb") as file_handler:
        ret = np.load(file_handler, allow_pickle=True).item()
        return ret


class Config:
    accents: typing.Dict[str, str]
    tones: collections.OrderedDict
    statistic: collections.OrderedDict
    grams_1: collections.OrderedDict
    grams_2: collections.OrderedDict
    size_1_gram: int
    total_count_1_gram: int
    max_word_length: int

    maxp: int
    """
        So luong tu lon nhat  trong cau
        """
    size_2_grams: int
    total_count_2_grams: int
    MIN: float
    space: bytes


__config__: typing.Optional[Config] = None
__accents_chars__ = (f"ÙÚỦỤŨƯỪỨỬỰỮ"
                     f"èéẻẹẽêềếểệễ"
                     f"òóỏọõôồốổộỗơờớởợỡ"
                     f"ÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ"
                     f"ùúủụũưừứửựữ"
                     f"àáảạãâầấẩậẫăằắẳặẵ"
                     f"ÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ"
                     f"ìíỉịĩÈÉẺẸẼÊỀẾỂỆỄ"
                     f"ỲÝỶỴỸÌÍỈỊĨ"
                     f"ỳýỷỵỹ")
__version__ = "0.0.0"

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


def get_config(dataset_path: str = None) -> Config:
    if dataset_path is None:
        dataset_path = os.path.join(__working_dir__, "share-storage", "dataset", pathlib.Path(__file__).name,
                                    __version__)
        if not os.path.isdir(dataset_path):
            os.makedirs(dataset_path, exist_ok=True)
    global __config__
    global __accents_chars__
    if not isinstance(__config__, Config):
        source_dir = pathlib.Path(__file__).parent.__str__()
        __config__ = Config()
        accent_data = [
            "UÙÚỦỤŨƯỪỨỬỰỮ",
            "eèéẻẹẽêềếểệễ",
            "oòóỏọõôồốổộỗơờớởợỡ",
            "OÒÓỎỌÕÔỒỐỔỘỖƠỜỚỞỢỠ",
            "uùúủụũưừứửựữ",
            "DĐ",
            "aàáảạãâầấẩậẫăằắẳặẵ",
            "dđ",
            "AÀÁẢẠÃÂẦẤẨẬẪĂẰẮẲẶẴ",
            "iìíỉịĩ",
            "EÈÉẺẸẼÊỀẾỂỆỄ",
            "YỲÝỶỴỸ",
            "IÌÍỈỊĨ",
            "yỳýỷỵỹ",
        ]
        lst = []
        __config__.accents = collections.OrderedDict()
        __config__.tones = {}
        _fx = {}

        for x in accent_data:

            for v in x:
                if not __config__.accents.get(x[0]):
                    __config__.accents[x[0]] = [v]
                else:
                    __config__.accents[x[0]].append(v)
                if __config__.tones.get(x[0]):
                    __config__.tones.get(x[0]).append(v)
                else:
                    __config__.tones[x[0]] = [v]
                lst.append(v)
                _fx[v] = x[0]

        __config__.tones = __load_data_from_zip__(os.path.join(source_dir, "vn_predictor_accents.npy.zip"),
                                                  dataset_path)
        __config__.statistic = __load_data_from_zip__(os.path.join(source_dir, "vn_predictor_stat.npy.zip"),
                                                      dataset_path)
        __config__.grams_1 = __load_data_from_zip__(os.path.join(source_dir, "vn_predictor_grams1.npy.zip"),
                                                    dataset_path)
        __config__.grams_2 = __load_data_from_zip__(os.path.join(source_dir, "vn_predictor_grams2.npy.zip"),
                                                    dataset_path)
        __config__.size_1_gram = 216448
        __config__.total_count_1_gram = 400508609.0
        __config__.maxp = 256
        __config__.size_2_grams = 5553699.0
        __config__.total_count_2_grams = 400508022.0
        __config__.MIN = -1000.0
        __config__.max_word_length = 8
        __config__.space = ' '.encode('utf8')

    return __config__


def __get_gram_count__(ngram_word, ngrams):
    if ngrams.get(ngram_word) is None:
        return 0
    output = ngrams[ngram_word]
    return output


def __replacer__(s, newstring, index, nofail=True):
    # insert the new string between "slices" of the original
    return s[:index] + newstring + s[index + 1:]


def __make_up_(input_str, possible_changes, current_len):
    global __config__
    if input_str[0] == 'd':
        len_ = current_len
        for i in range(len_):
            word = possible_changes[i]
            nword = 'đ' + word[1:]
            if __config__.grams_1.get(nword):
                possible_changes[current_len] = nword
                current_len += 1

    return possible_changes, current_len


def __generate_variety__(input_str: str, index, possible_changes, current_len):
    global __config__
    # # input_str="chuong"
    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    start = -1
    end = -1
    i = 0
    for c in input_str:
        for x in vowels:
            if x == c:
                if start == -1:
                    start = i
                if end < i:
                    end = i

        i += 1
    if start == -1 or end == -1:
        if __config__.grams_1.get(input_str):
            possible_changes[current_len] = input_str
            possible_changes, current_len = __make_up_(input_str, possible_changes, current_len)
        return possible_changes, current_len
    key = input_str[start:end + 1]
    lst = __config__.tones.get(key)
    if not lst:
        if __config__.grams_1.get(input_str):
            possible_changes[current_len] = input_str
            current_len += 1
            possible_changes, current_len = __make_up_(input_str, possible_changes, current_len)
        return possible_changes, current_len
    current_len = 0
    for x in lst:
        v_word = input_str[0:start] + x + input_str[end + 1:]
        if __config__.grams_1.get(v_word):
            possible_changes[current_len] = v_word
            current_len += 1
    possible_changes, current_len = __make_up_(input_str, possible_changes, current_len)
    return possible_changes, current_len


def __process_out_put__(input_string, output_string):
    input_string = input_string.lstrip(' ').rstrip(' ').replace('  ', ' ')
    string_builder = ""
    len_of_input = len(input_string)
    len_of_out_put = len(output_string)
    for i in range(len_of_input):
        input_char = input_string[i]
        output_char = " "
        if i < len_of_out_put:
            output_char = output_string[i]

        if input_char.isupper():
            string_builder += output_char.upper()
        else:
            string_builder += output_char

    return string_builder


def __normalize_string__(input_str):
    output = input_str.replace("[\t\"\':\\(\\)]", " ")
    output = output.replace("\\s{2,}", " ")
    return output.strip()


def predict_accents(input_content):
    global __config__
    if __config__ is None:
        get_config()
    input_sentences = re.split("[.!?,\n;?]", input_content)
    output = ""
    result = ""
    for input_sentence in input_sentences:
        # set_possible_changes()
        in_ = __normalize_string__(input_sentence)
        lowercase_in = in_.lower()
        words = lowercase_in.split(" ")
        words = [x for x in words if x.rstrip(' ').rstrip(' ') != ""]
        len_of_words = len(words)
        if len_of_words == 0:
            continue

        numberP = numpy.zeros(len_of_words, dtype=int)
        trace = numpy.zeros((len_of_words, __config__.maxp), dtype=int)
        Q = numpy.zeros((len_of_words, __config__.maxp), dtype=float)
        possible_change = [[""] * __config__.maxp for _ in range(len_of_words)]
        # possible_change = np.full((len_of_words, __config__.maxp,__config__.max_word_length), "".encode('utf8'), dtype=bytes)

        for i in range(len_of_words):
            num_of_word_processing = 0
            _, num_of_word_processing = __generate_variety__(words[i], 0, possible_change[i], num_of_word_processing)
            possible_change[i][num_of_word_processing] = words[i]
            num_of_word_processing += 1
            numberP[i] = num_of_word_processing

        if len_of_words == 1:
            max = 0
            sure = words[0]
            for i in range(numberP[0]):
                possible = possible_change[0][i]
                number1GRam = __get_gram_count__(possible, __config__.grams_1)
                if max < number1GRam:
                    max = number1GRam
                    sure = possible
            output += sure.strip() + "\n"
        else:
            for i1 in range(1, len_of_words):
                recent_possible_num = numberP[i1]
                old_possible_num = numberP[i1 - 1]
                for j in range(recent_possible_num):
                    Q[i1][j] = __config__.MIN
                    temp = __config__.MIN
                    for k1 in range(old_possible_num):
                        new_word = possible_change[i1][j]
                        old_word = possible_change[i1 - 1][k1]
                        log = -100.0

                        number2Gram = __get_gram_count__(old_word + " " + new_word, __config__.grams_2)
                        number1Gram = __get_gram_count__(old_word, __config__.grams_1)
                        if number1Gram > 0 and number2Gram > 0:
                            log = math.log((number2Gram + 1) / (number1Gram + __config__.statistic[old_word]))
                        else:
                            log = math.log(1.0 / (2 * (__config__.size_2_grams + __config__.total_count_2_grams)))

                        if i1 == 1:
                            log += math.log(
                                (number1Gram + 1) / (__config__.size_1_gram + __config__.total_count_1_gram))
                        if temp != Q[i1 - 1][k1]:
                            if temp == __config__.MIN:
                                temp = Q[i1 - 1][k1]
                        value = Q[i1 - 1][k1] + log

                        if Q[i1][j] < value:
                            # print(f"{old_word} {new_word} -> {value}")
                            Q[i1][j] = value
                            trace[i1][j] = k1
            max = __config__.MIN
            k = 0

            for l in range(numberP[len_of_words - 1]):
                if max <= Q[len_of_words - 1][l]:
                    max = Q[len_of_words - 1][l]
                    k = l
                    # print(possible_change[len(words) - 1][k])
            result = possible_change[len_of_words - 1][k]
            k = trace[len_of_words - 1][k]
            i = len_of_words - 2
            while i >= 0:
                result = possible_change[i][k] + " " + result
                k = trace[i][k]
                i = i - 1
        output += __process_out_put__(input_sentence, result) + "\n"
        del possible_change
        del Q
        del numberP
        del trace

    return output.strip()


def is_accent_word(word: str):
    global __config__
    if __config__ is None:
        get_config()
    for x in word:
        if x in __accents_chars__:
            return True
    return False




def vn_clear_sticky(unknown_word: str) -> typing.List[str]:
    ret= []
    unclear_words = seperate_words_clear(unknown_word)
    unclear_word = unclear_words[0]
    len_of_unclear_word = len(unclear_word)
    first_word = unclear_word
    process_len =0
    for i in range(0, len_of_unclear_word):
        word_from_right = unclear_word[0:len_of_unclear_word - i]
        if __config__.grams_1.get(word_from_right.lower()):
            first_word = word_from_right
            break
    ret +=[first_word]
    process_len+=len(first_word)
    len_of_unclear_words = len(unclear_words)
    tmp_unclear= None
    for index in range(1,len_of_unclear_words):
        unclear_word = unclear_words[index]
        tmp_unclear = unclear_word
        len_of_unclear_word = len(unclear_word)
        max_val =-1
        next_word = None
        if unclear_word=="nhthứcL":
            vx = unclear_word
        for i in range(0, len_of_unclear_word):
            word_from_left = unclear_word[i:]
            if word_from_left=="thứcL":
                fx=1

            check_word = (first_word+" "+word_from_left).lower()
            val = __config__.grams_2.get(check_word)
            if val  and val>max_val:
                max_val = val
                next_word = word_from_left
            for k in range(1,len_of_unclear_word-i):
                word_from_right = word_from_left[0:len_of_unclear_word-i-k]
                check_word = (first_word + " " + word_from_right).lower()
                val = __config__.grams_2.get(check_word)

                # number2Gram = __get_gram_count__(old_word + " " + new_word, __config__.grams_2)
                # number1Gram = __get_gram_count__(old_word, __config__.grams_1)
                # if number1Gram > 0 and number2Gram > 0:
                #     log = math.log((number2Gram + 1) / (number1Gram + __config__.statistic[old_word]))
                # else:
                #     log = math.log(1.0 / (2 * (__config__.size_2_grams + __config__.total_count_2_grams)))
                #
                # if i1 == 1:
                #     log += math.log(
                #         (number1Gram + 1) / (__config__.size_1_gram + __config__.total_count_1_gram))
                # if temp != Q[i1 - 1][k1]:
                #     if temp == __config__.MIN:
                #         temp = Q[i1 - 1][k1]
                # value = Q[i1 - 1][k1] + log

                if val is None:
                    vx= val
                suggests_word = None
                if val is None and not is_accent_word(word_from_right):
                    sentence = ret[ret.__len__()-1]+" "+word_from_right
                    suggests_word = predict_accents(sentence)

                    if suggests_word.split(' ')[1] != word_from_right:
                        val = __config__.grams_2.get(suggests_word)
                        ret[ret.__len__() - 1] = suggests_word.split(' ')[0]
                        suggests_word = suggests_word.split(' ')[1]
                        next_word = suggests_word
                        word_from_right = suggests_word

                if val and val > max_val:
                    max_val = val*(10**len(word_from_right))
                    next_word = word_from_right
        if next_word!= None:
            ret+=[next_word]
            process_len += len(next_word)
        else:
            ret+=[tmp_unclear]
            process_len += len(tmp_unclear)
        first_word = next_word
    if process_len<len(unknown_word):
        ret+=[unknown_word[process_len:]]
    print(unknown_word)
    print(ret)

def correct_accents(input_content):
    global __config__
    if __config__ is None:
        get_config()
    input_sentences = re.split("[.!?,\n;?]", input_content)
    output = ""
    result = ""
    for input_sentence in input_sentences:
        # set_possible_changes()
        in_ = __normalize_string__(input_sentence)
        lowercase_in = in_.lower()
        words = lowercase_in.split(" ")
        words = [x for x in words if x.rstrip(' ').rstrip(' ') != ""]
        len_of_words = len(words)
        if len_of_words == 0:
            continue

        numberP = numpy.zeros(len_of_words, dtype=int)
        trace = numpy.zeros((len_of_words, __config__.maxp), dtype=int)
        Q = numpy.zeros((len_of_words, __config__.maxp), dtype=float)
        possible_change = [[""] * __config__.maxp for _ in range(len_of_words)]
        # possible_change = np.full((len_of_words, __config__.maxp,__config__.max_word_length), "".encode('utf8'), dtype=bytes)

        for i in range(len_of_words):
            num_of_word_processing = 0
            if is_accent_word(words[i]) and __config__.grams_1.get(words[i]):
                possible_change[i][num_of_word_processing] = words[i]
                num_of_word_processing += 1
                numberP[i] = num_of_word_processing
            else:
                _, num_of_word_processing = __generate_variety__(words[i], 0, possible_change[i],
                                                                 num_of_word_processing)
                possible_change[i][num_of_word_processing] = words[i]
                num_of_word_processing += 1
                numberP[i] = num_of_word_processing

        if len_of_words == 1:
            max = 0
            sure = words[0]
            for i in range(numberP[0]):
                possible = possible_change[0][i]
                number1GRam = __get_gram_count__(possible, __config__.grams_1)
                if max < number1GRam:
                    max = number1GRam
                    sure = possible
            output += sure.strip() + "\n"
        else:
            for i1 in range(1, len_of_words):
                recent_possible_num = numberP[i1]
                old_possible_num = numberP[i1 - 1]
                for j in range(recent_possible_num):
                    Q[i1][j] = __config__.MIN
                    temp = __config__.MIN
                    for k1 in range(old_possible_num):
                        new_word = possible_change[i1][j]
                        old_word = possible_change[i1 - 1][k1]
                        log = -100.0

                        number2Gram = __get_gram_count__(old_word + " " + new_word, __config__.grams_2)
                        number1Gram = __get_gram_count__(old_word, __config__.grams_1)
                        if number1Gram > 0 and number2Gram > 0:
                            log = math.log((number2Gram + 1) / (number1Gram + __config__.statistic[old_word]))
                        else:
                            log = math.log(1.0 / (2 * (__config__.size_2_grams + __config__.total_count_2_grams)))

                        if i1 == 1:
                            log += math.log(
                                (number1Gram + 1) / (__config__.size_1_gram + __config__.total_count_1_gram))
                        if temp != Q[i1 - 1][k1]:
                            if temp == __config__.MIN:
                                temp = Q[i1 - 1][k1]
                        value = Q[i1 - 1][k1] + log

                        if Q[i1][j] < value:
                            # print(f"{old_word} {new_word} -> {value}")
                            Q[i1][j] = value
                            trace[i1][j] = k1
            max = __config__.MIN
            k = 0

            for l in range(numberP[len_of_words - 1]):
                if max <= Q[len_of_words - 1][l]:
                    max = Q[len_of_words - 1][l]
                    k = l
                    # print(possible_change[len(words) - 1][k])
            result = possible_change[len_of_words - 1][k]
            k = trace[len_of_words - 1][k]
            i = len_of_words - 2
            while i >= 0:
                result = possible_change[i][k] + " " + result
                k = trace[i][k]
                i = i - 1
        output += __process_out_put__(input_sentence, result) + "\n"
        del possible_change
        del Q
        del numberP
        del trace

    return output.strip()
