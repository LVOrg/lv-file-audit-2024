import collections
import datetime
import pathlib
import os
import threading

import numpy as np
import cy_vn_suggestion.settings
import zipfile
import numpy
from cy_vn_suggestion.settings import (
    Config,
    __tones__,
    __remove_gram_1_words,
    __config__,
    __invalid_end__,
    __invalid_start_1__)
from cy_vn_suggestion import __version__

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


__resource_loader_lock__ = threading.Lock()


def __get_config__(dataset_path: str = None) -> cy_vn_suggestion.settings.Config:
    __version__dir_name__ = __version__.replace(".", "_")
    if dataset_path is None:
        dataset_path = os.path.join(__working_dir__, "share-storage", "datasets", pathlib.Path(__file__).stem,
                                    __version__dir_name__)
        if not os.path.isdir(dataset_path):
            os.makedirs(dataset_path, exist_ok=True)
    start_load_at = datetime.datetime.now()

    global __config__
    global __accents_chars__
    global __tones_ignore__
    if not isinstance(__config__, Config):
        source_dir = pathlib.Path(__file__).parent.__str__()
        source_dir = os.path.join(source_dir, "data", __version__dir_name__)
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
    n = datetime.datetime.now() - start_load_at
    print(f"load data from {dataset_path}, in {n.total_seconds()} second(s)")
    return __config__


def get_config(reload: bool = False) -> Config:
    global __config__
    global __resource_loader_lock__
    if reload:
        __config__ = None
    if __config__ is None:
        __resource_loader_lock__.acquire()
        __get_config__()

        total_removed_items_in_grams_1 = 0
        # grams_1_keys = list(__config__.grams_1.keys())
        # for k in grams_1_keys:
        #     if len(k) >= 2 and k[-2] in __invalid_end__:
        #         if __config__.grams_1.get(k):
        #             del __config__.grams_1[k]
        #             total_removed_items_in_grams_1 += 1
        #     if len(k) >= 1 and (k[-1] in __invalid_end__) or (k[0] in __invalid_start_1__):
        #         if __config__.grams_1.get(k):
        #             del __config__.grams_1[k]
        #             total_removed_items_in_grams_1 += 1
        # print(f"Total {total_removed_items_in_grams_1} items removed in grams_1")
        # for x in __remove_gram_1_words:
        #     if __config__.grams_1.get(x):
        #         del __config__.grams_1[x]
        __resource_loader_lock__.release()
    return __config__
