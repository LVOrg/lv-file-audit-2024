import math
import os
import pathlib
import re
import typing
import numpy
import zipfile
import collections
import numpy as np
import threading
import phunspell

vn_spell = phunspell.Phunspell("vi_VN")
__version__ = "0.0.0.3"
__working_dir__ = pathlib.Path(__file__).parent.parent.parent.__str__()

__resource_loader_lock__ = threading.Lock()


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
__clear_accents_map__ = {'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ụ': 'U', 'Ũ': 'U', 'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U',
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
__clear_accents_map__.update({
    'e': 'e', 'y': 'y', 'u': 'u', 'i': 'i', 'o': 'o', 'a': 'a',
    'E': 'E', 'Y': 'Y', 'U': 'U', 'I': 'I', 'O': 'O', 'A': 'A'
})
__tones__ = {
    "iay": ["iẩy", "iâý", "iẫy", "iay", "iấy", "iày", "ìay", "iầy", "iáy", "iãy", "iạy", "iây", "iảy"],
    "uy": ["ùy", "uý", "uỹ", "uy", "úy", "ụy", "uỳ", "ũy", "ủy", "uỵ", "uỷ"],
    "oa": ["oâ", "oẳ", "oặ", "oà", "óa", "õa", "oằ", "oẫ", "oã", "ọa", "oắ", "oă", "oả", "oẵ", "òa", "oa", "ỏa", "oạ",
           "oá"],
    "oi": ["ối", "ỏi", "ọi", "ời", "ói", "ỡi",
           "õi", "ợi", "ôi", "ồi", "òi", "ơí", "ơi", "oi", "ỗi",
           "ổi", "ội", "ởi", "ới"],
    "a": ["ạ", "ã", "â", "ẳ", "ặ", "a", "ẩ", "ấ", "ă", "ả", "à", "ẵ", "á", "ắ", "ẫ", "ằ", "ầ", "ậ"],
    "ua": ["uậ", "uă", "ưa", "uặ", "uắ", "úa", "ửa", "uẵ", "uẩ", "uá", "ùa", "ứa", "uẫ", "uà", "ũa", "ụa", "uầ", "ủa",
           "uấ", "uẳ", "uạ", "uả", "uằ", "ừa", "uã", "ựa", "ữa", "uâ", "ua"],
    "o": ["ớ", "ỗ", "ổ", "ơ", "ố", "ò", "õ", "ộ", "ở", "ô", "ợ", "ọ", "ỡ", "ỏ", "o", "ồ", "ó", "ờ"],
    "uu": ["ứu", "ựu", "ưu", "ửu", "ữu", "ừu"],
    "uo": ["ưở", "uỡ", "uớ", "ượ", "ưỡ", "uở", "ươ", "uờ", "uổ", "uỗ", "uô", "ườ", "ướ", "uồ", "uộ", "uợ", "uơ", "uố",
           "uọ"],
    "eo": ["ểo", "ẽo", "èo", "ẹo", "ẻo", "éo", "eo"],
    "oai": ["oai", "oải", "oàì", "oài", "oái", "oại", "oãi"],
    "yeu": ["yễu", "yêu", "yểu", "yệu", "yếu", "yeu", "yều"],
    "uou": ["ượu", "ươu"],
    "uoi": ["uội", "uôí", "uồi", "uổi", "uối", "ười", "ướí", "ườì", "ưỡi", "ượi", "uoi", "uỗi", "ươi", "ưới", "uôi"],
    "ieu": ["iểu", "iếu", "iệu", "iễu", "iêu", "iều"],
    "uay": ["uậy", "uảy", "uây", "uẩy", "uầy", "uấy", "uay", "uẫy", "uày"],
    "iu": ["iủ", "iụ", "iử", "iứ", "ỉu", "iư", "iừ", "íu", "ìu", "iú", "iữ", "iự", "iu", "ĩu", "iù", "ịu", "iũ"],
    "ia": ["iă", "ĩa", "iấ", "iặ", "iả", "ỉa", "iẳ", "iẵ", "iậ", "iắ", "iâ", "iầ", "iã", "iá", "iạ", "ịa", "ìa", "ià",
           "ía", "iẩ", "iằ", "iẫ", "ia"],
    "ou": ["ơu", "ớu", "ởu"],
    "ueo": ["ueo", "uẹo", "uéo", "uèo"],
    "ui": ["ừi", "ửi", "ữi", "ùi", "úi", "ũi", "ui", "ủi", "ưi", "ứi", "ựi", "uì", "ụi"],
    "iuo": ["iướ", "iươ", "iưò", "iuố", "iuộ", "iuồ", "iưỡ", "iườ", "iượ", "iưở"],
    "io": ["iỏ", "iồ", "iỡ", "iô", "iợ", "iố", "iộ", "iơ", "iọ", "ío", "io", "iờ", "iớ", "iỗ", "iở", "iò", "iổ", "iõ",
           "ió"],
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

count_ = 0


def __get_config__(dataset_path: str = None) -> Config:
    global __version__
    __version__dir_name__ = __version__.replace(".", "_")
    if dataset_path is None:
        dataset_path = os.path.join(__working_dir__, "share-storage", "datasets", pathlib.Path(__file__).stem,
                                    __version__dir_name__)
        if not os.path.isdir(dataset_path):
            os.makedirs(dataset_path, exist_ok=True)
    print(f"dataset path {dataset_path}")
    global __config__
    global __accents_chars__
    global __tones_ignore__
    if not isinstance(__config__, Config):
        source_dir = pathlib.Path(__file__).parent.__str__()
        source_dir = os.path.join(source_dir, "vn_data", __version__dir_name__)
        print(f"source dir from lib -> {source_dir}")
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

        __config__.tones = __tones__
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

    f_check = 'euioa'
    _l = []
    for x in f_check:
        for y in f_check:
            for z in f_check:
                if __config__.tones.get(x + y + z):
                    _l += __config__.tones.get(x + y + z)
                    if len(_l) > 10:
                        _l = []

    return __config__


__remove_gram_1_words = ["trườmg","tromg"]


def get_config():
    global __config__
    global __resource_loader_lock__
    if __config__ is None:
        __resource_loader_lock__.acquire()
        __get_config__()
        __invalid_end__ = ["mg"]
        total_removed_items_in_grams_1 = 0
        grams_1_keys = list(__config__.grams_1.keys())
        for k in grams_1_keys:
            if len(k)>=2 and k[-2] in __invalid_end__:
                del __config__.grams_1[k]
                total_removed_items_in_grams_1+=1
        print(f"Total {total_removed_items_in_grams_1} items removed in grams_1")
        for x in __remove_gram_1_words:
            if __config__.grams_1.get(x):
                del __config__.grams_1[x]
        __resource_loader_lock__.release()


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


def __clear_accents__(w):
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
        r += clear_map.get(c, c)
    return r


def __is_valid_vn_word__(w: str):
    __check_first__ = ["z", "w", "f", "j", "f"]
    __check_last__ = ["q", "w", "r", "s", "d", "đ", "f", "j", "k", "l", "z", "x", 'v', 'b']
    __validator_last_2_letter__ = ["ch", "nh", "ng"]
    __first_map__ = {
        "t": ["h", "r"],
        "n": ["g", "h"],
        "p": ["h"],
        "g": ["h"],
        "k": ["h"],
        "c": ["h"],
        "n": ["h"]
    }
    start_vowel = -1
    __pre__ = [""]
    len_of_w = len(w)
    if len_of_w <= 1: return True
    if w[0] in __check_first__:
        return False
    if w[-1] in __check_last__:
        return False
    if not __first_map__.get(w[0]):
        if w[1] not in __full_accents__:
            return False
    has_vowel = False
    for i in range(0, len_of_w):
        if w[i] in __full_accents__:
            if start_vowel == -1: start_vowel = i
            has_vowel = True
            if i + 1 > len_of_w:
                raise NotImplemented()
            for k in range(i + 1, len_of_w):
                if w[k] in __full_accents__:
                    if w[k - 1] not in __full_accents__:
                        return False
                    if len_of_w - k - 1 == 2:
                        return w[k + 1:] in __validator_last_2_letter__
                    check_accents = __clear_accents_map__[w[i]] + __clear_accents_map__[w[k]]
                    if k + 1 < len_of_w and w[k + 1] in __full_accents__:
                        return __config__.tones.get(check_accents + __clear_accents_map__[w[k + 1]]) is not None
                    return __config__.tones.get(check_accents) is not None

            if i == 3:
                return w[0:i] == "ngh"
            if i == 2:
                return w[1] in __first_map__.get(w[0], [])

            return has_vowel
    return has_vowel


def __generate_variety__(input_str: str, index, possible_changes, current_len, use_phunspell_suggest):
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
        elif use_phunspell_suggest and not __is_valid_vn_word__(input_str):
            for suggest_word in vn_spell.suggest(input_str):
                possible_changes[current_len] = suggest_word
                current_len += 1
            if input_str[0] == 'd':
                for suggest_word in vn_spell.suggest('đ' + input_str[1:]):
                    possible_changes[current_len] = suggest_word
                    current_len += 1
        return possible_changes, current_len
    key = input_str[start:end + 1]
    lst = __config__.tones.get(key)
    if not lst:
        if __config__.grams_1.get(input_str):
            possible_changes[current_len] = input_str
            current_len += 1
            possible_changes, current_len = __make_up_(input_str, possible_changes, current_len)
        elif use_phunspell_suggest and not __is_valid_vn_word__(input_str):
            for suggest_word in vn_spell.suggest(input_str):
                possible_changes[current_len] = suggest_word
                current_len += 1
            if input_str[0] == 'd':
                for suggest_word in vn_spell.suggest('đ' + input_str[1:]):
                    possible_changes[current_len] = suggest_word
                    current_len += 1
        return possible_changes, current_len
    current_len = 0
    for x in lst:
        v_word = input_str[0:start] + x + input_str[end + 1:]
        if __config__.grams_1.get(v_word):
            possible_changes[current_len] = v_word
            current_len += 1
        elif use_phunspell_suggest and not __is_valid_vn_word__(v_word):
            for suggest_word in vn_spell.suggest(v_word):
                if suggest_word not in possible_changes:
                    possible_changes[current_len] = suggest_word
                    current_len += 1
            if v_word[0] == 'đ':
                for suggest_word in vn_spell.suggest('đ' + v_word[1:]):
                    if suggest_word not in possible_changes:
                        possible_changes[current_len] = suggest_word
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


def predict_accents(input_content, use_phunspell_suggest=True):
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

        for i in range(len_of_words):
            num_of_word_processing = 0
            _, num_of_word_processing = __generate_variety__(words[i], 0, possible_change[i], num_of_word_processing,
                                                             use_phunspell_suggest)
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


def check_word(word: str):
    get_config()
    return __config__.grams_1.get(word)
