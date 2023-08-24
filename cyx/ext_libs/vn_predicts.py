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

__version__ = "0.0.0.0"
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

__tones_ignore__ = [
    'ữõ', 'ưò', 'ủạ', 'ựạ', 'ứá', 'ữạ', 'ủả', 'ụá', 'ưầ', 'ửả', 'ụậ', 'êù', 'ếú', 'êú', 'ựạ', 'ứá', 'ưả', 'ủạ', 'ưỏ',
    'ưà', 'ưá',
    'ưồ', 'ưô', 'ưộ', 'ưố', 'ụộ', 'ưo', 'ưọ', 'ùo', 'ưổ',
    'ửá', 'ưà', 'eu', 'êừ', 'ưã', 'ụo', 'iêú', 'iềụ',
    'iếú', 'ìeu', 'iềủ', 'iềù', 'iêũ', 'iêụ', 'iểù', 'iềú', 'ỉeu', 'iêù', 'iệụ'
                                                                          'ưyê', 'ưyễ',
    'ỉệ', 'ìệ', 'ịệ',
    'aủ', 'ậụ', 'âử', 'âú', 'ầù', 'âủ', 'aư', 'àù', 'âù', 'âụ', 'âư', 'âũ',
    'ợo', 'ơơ', 'óo', 'òo', 'ỏó', 'ôộ', 'ọọ', 'ơợ', 'oó', 'òò', 'oỏ', 'ôố', 'oợ', 'ôồ', 'oọ', 'oộ', 'oo', 'ơờ', 'ơở',
    'oò', 'ơộ', 'ôỗ', 'oô', 'oồ', 'ôổ', 'oổ', 'ôô', 'oố',
    'aở', 'âo', 'ằo',
    'àò', 'ảỏ', 'aõ', 'áó', 'àô', 'ắo', 'aồ', 'àọ', 'áọ', 'aỏ', 'ăộ', 'ấo', 'ậo', 'ăo', 'ạọ', 'ão',
    'ôá', 'ớá', 'ốa', 'ởã', 'ơa', 'ổà', 'ôă', 'ôẩ', 'ọạ', 'óá', 'ọả', 'ơả', 'ốá', 'ồa', 'oẫ', 'ôa', 'ơạ', 'òà',
    'àò', 'ảỏ', 'aõ', 'áó', 'àô', 'ắo', 'aồ', 'àọ', 'áọ', 'aỏ', 'ăộ', 'ấo', 'ậo', 'ăo', 'ạọ',
    'ôá', 'ớá', 'ốa', 'ởã', 'ơa', 'ổà', 'ôă', 'ôẩ', 'ọạ', 'oâ', 'óá', 'ọả', 'ơả', 'ốá', 'ồa', 'oẫ', 'ôa', 'oả', 'ơạ',
    'òà',
    'àò', 'ảỏ', 'aõ', 'áó', 'àô', 'ắo', 'aồ', 'àọ', 'áọ', 'aỏ', 'ăộ', 'áo', 'ấo', 'ậo', 'ăo', 'ạọ', 'ão',
    'ịe', 'íe', 'ĩe', 'ie', 'ìe', 'iẻ', 'ỉe', 'iẽ', 'iè',
    'ộí', 'ôỉ', 'ôĩ', 'ớỉ', 'ọị', 'ơì', 'ờì', 'ớí', 'ôì', 'ờĩ', 'ôị', 'ơị', 'ộị', 'ôí', 'ơỉ', 'ờị', 'ồì', 'ợị',
    'óí', 'ổỉ', 'ổi', 'ởỉ', 'ốí']
__tones_ignore__ = ['eể', 'êe', 'eẻ', 'eé', 'êệ', 'ẻe', 'ee', 'eế', 'eê', 'êê', 'eè']
__tones_ignore__ += ['ẻu', 'ễu', 'éu']
__tones_ignore__ += ['ếi', 'ẻi', 'êi', 'éi', 'ei', 'ềì', 'ềi']
__tones_ignore__ += ['ếo', 'eô', 'êở', 'eó', 'êô', 'eơ', 'êo', 'eở', 'ẽọ', 'ệo', 'êỏ']
__tones_ignore__ += ['êa', 'eà', 'eạ', 'eã', 'ea', 'ểa', 'eắ', 'êầ', 'êà', 'eậ', 'êả', 'ếa',
                     'êạ', 'eẩ', 'eẳ', 'eấ', 'êậ', 'eá']
__tones_ignore__ += ['ưụ', 'úú', 'ưú', 'ưư', 'ưữ', 'ưự', 'uự', 'úu', 'ủủ',
                     'úù', 'ùu', 'ụu', 'ũu', 'ưù', 'ưũ', 'ủu']
__tones_ignore__ += ['ữỉ', 'ụị', 'uỉ', 'uĩ', 'uị', 'uí', 'ưỉ']
__tones_ignore__ += ['úo', 'uo', 'ửo', 'ưó']
__tones_ignore__ += ['íi', 'ỉi', 'ịị', 'ìi', 'ĩi', 'ii', 'ìì']
__tones_ignore__ += ['ởe', 'ôe', 'ơẻ', 'ơe', 'ôé']
__tones_ignore__ += ['ơừ', 'õu', 'ou', 'ỏũ', 'ỏu', 'òu', 'óu']
__tones_ignore__ += ['aé', 'aê', 'ae']
__tones_ignore__ += ['aa', 'aạ', 'aẩ', 'ăà', 'ăa', 'âa', 'aà', 'âậ', 'aằ', 'âạ', 'ăặ', 'aầ',
                     'aậ', 'aá', 'aả', 'aâ', 'aắ', 'aã', 'ăằ']
__tones_ignore__ += ['ạị', 'ảí', 'ạỉ', 'ảỉ', 'âỉ', 'aỉ', 'aị', 'áí']
__tones_ignore__ += ['eee']
__tones_ignore__+=['êẻò', 'eeo']
__tones_ignore__+=['eue', 'eủe']
__tones_ignore__+=['euu', 'eui','euo','êuở','eua','eie','eiu','eii','eio']+['eía', 'eia']
__tones_ignore__+=['eeu', 'êệu', 'eei', 'eea', 'eõe', 'eoe', 'eou', 'eoi', 'eoô', 'eoo', 'eoa']
__tones_ignore__+=['eae', 'eau', 'eai', 'eão', 'eao', 'eaa', 'uee', 'uều', 'ueu', 'uệu', 'uei']
__tones_ignore__+=['uea', 'ueá', 'uêa', 'uuu', 'ưũi', 'uui', 'ưướ', 'ưuo', 'ưườ', 'uướ', 'uườ', 'uuộ', 'uuo', 'uượ']
__tones_ignore__+=['uuấ', 'ưửa', 'ưuẩ', 'uủa', 'uua', 'ưùa', 'uiề', 'ưíế', 'uiể', 'uie', 'uiu', 'uíu']
__tones_ignore__+=['ưỉi', 'uii', 'uio', 'ưiớ', 'uiờ', 'uia', 'uỉa', 'uoe', 'uou',
                   'ượụ', 'ưởu', 'uợu', 'ưỡu', 'ươụ', 'ườu', 'ưọu', 'ướu', 'uơu']
__tones_ignore__+=['uôỉ',  'úoi', 'uơi', 'uôì', 'uỡi', 'uời',
                   'ưoi', 'ườị', 'ươí', 'ưội','ườỉ', 'uộỉ',
                   'ưói','ưòi', 'ưổi',  'uởi', 'ượì', 'ủoi', 'uới', 'ùoi', 'ươì', 'ưởi']
__tones_ignore__+=['uoo', 'uoa', 'ướá', 'uốá', 'uoặ', 'uoá', 'uoă',
                   'uaẻ', 'ủae', 'uae', 'uau', 'uẫu', 'uầu', 'uảu','ủau']
__tones_ignore__+=[ 'ưai', 'ủai', 'úai', 'ùai',
                    'uaổ', 'uầo', 'uaố', 'uaô', 'ủao']
__tones_ignore__+=['ưaá', 'ưaà', 'ưaa', 'ưaả', 'uaa', 'uaả', 'uaá', 'ủaa', 'iee', 'iêệ', 'iêế']
__tones_ignore__+=['íeu', 'iêủ','ịeu', 'ieu', 'iệụ']
__tones_ignore__+=['iei', 'iệi', 'ỉei', 'iêì', 'iếo', 'iềo', 'iệo','iea', 'iêa']
__tones_ignore__+=['iuệ', 'iue', 'iữu', 'iuu','iui']
__tones_ignore__+=['iũa', 'íua', 'iưã', 'iưẫ']
__tones_ignore__+=['iiê', 'iiề', 'iìe', 'iie', 'iiế', 'iiệ', 'iiu', 'iiữ', 'iii', 'iio', 'iia', 'iía', 'iỉa']
__tones_ignore__+=['ioe', 'iòe', 'iou', 'iơi', 'iợi', 'ioi', 'iổi', 'ióí', 'iồi',  'iỏị', 'iơí',
                   'iõi', 'iội', 'iối', 'iởi', 'iói', 'iòi', 'iọi', 'iỏỉ', 'iỗi']
__tones_ignore__+=['ioỏ', 'ioó', 'ioo', 'ióa', 'ioá', 'ioă', 'ioa', 'ioã', 'iơầ', 'iaế', 'iae']

__tones_ignore__+=['iáu', 'iâu', 'iầu', 'iau', 'iấu', 'iẩu', 'iậu', 'iáù', 'ìau', 'iảu']
__tones_ignore__ +=[ 'iăi', 'ỉai',   'iáó', 'íao']
__tones_ignore__+=['iaa', 'iaả', 'iaà', 'oee', 'ơẻu', 'oeu', 'oei', 'oèo', 'oẹo', 'oéo', 'oẻo', 'oeo', 'ôèo']
__tones_ignore__+=['oeả', 'oea', 'oue', 'ouu', 'oủi', 'oui', 'ôùi', 'ouộ', 'oua', 'oie', 'oỉe', 'ôịe', 'ơỉe', 'ơiệ']
__tones_ignore__+=['ơiừ', 'ôiứ', 'oiu', 'oiư', 'ơỉu', 'ơiu', 'ôĩì', 'ôịi', 'ôii', 'ôìi', 'ôíi', 'ơíi', 'oịi',
                   'ôĩi', 'oỉi', 'oii', 'ơìi', 'ôỉi']
__tones_ignore__+=['oio', 'ờiô', 'ơiố', 'oĩo', 'ơiở', 'oỉả', 'ơía', 'ôịả', 'ơỉa',
                   'oia', 'oiâ', 'oịá', 'ớia', 'ơiấ', 'oìa', 'ôiầ']
__tones_ignore__+=['ôoé', 'ooe', 'oou', 'oời', 'oọi', 'oới', 'oòì', 'ooi', 'oói', 'ơời', 'ơới']
__tones_ignore__+=['ooo', 'ooố', 'oỏa', 'ooặ', 'oòa', 'oòà', 'ooa', 'ooà', 'oae',
                   'oau', 'oạị', 'oảỉ', 'ơáí','oăi']
__tones_ignore__+=['ôáỏ', 'oáó', 'ơàỏ', 'oào', 'oão', 'oao', 'oáo', 'oaa', 'oaà', 'oaá', 'oaâ']
__tones_ignore__+=['aêê', 'aee', 'aeu', 'aei', 'aeo', 'aeá', 'aea', 'aue', 'âũe', 'auể', 'aúe', 'âủe']
__tones_ignore__+=['aừu', 'àuu', 'auu', 'aui', 'aùi', 'âuở', 'auo', 'auở', 'aứa', 'âúa', 'aửa', 'auậ', 'aúa', 'auâ', 'aua']
__tones_ignore__+=['aịe', 'aie', 'aiu', 'âìu', 'aìu', 'aịụ', 'aỉu', 'aịu', 'aii', 'aỉi', 'aĩi', 'aịi']
__tones_ignore__+=['aiở', 'ảiở', 'aịo', 'aio', 'aiô', 'aìa', 'aia', 'aiặ', 'aỉa', 'aoe', 'âộù', 'aou']
__tones_ignore__+=['aoi', 'aòi', 'aỏi', 'aọi', 'aoố', 'aoo', 'aòo', 'aoa', 'aae', 'aãù', 'aau', 'aâu']
__tones_ignore__+=['ôấy', 'ôẩý','dụệ','đêở']
__tones_ignore__+=['đôỉ', 'đôị', 'đơị',
                   'dôí', 'đốí',
                   'đơì','đổỉ', 'độị','dơì']
__tones_ignore__+=['dìe','dĩe', 'dịe', 'địệ', 'địe', 'đỉe','díe']
__tones_ignore__+=['dạỵ', 'đâỷ', 'dâỵ',
                   'đằy', 'đâỳ']
__tones_ignore__+=['ũay', 'ụay', 'ưẩý','úay', 'uáy']
__tones_ignore__+=['đêử', 'đềụ', 'deu',  'đêù']
__tones_ignore__+=[ 'độa',  'đôặ', 'đóá',  'dọạ', 'đõa']
__tones_ignore__+=['đậi','dạị', 'đầi', 'đâi', 'đạị',  'dầi', 'đăị']
__tones_ignore__+=['đừi']
__tones_ignore__+=['đưô', 'đụo', 'dưo', 'dụo', 'dưộ', 'đuợ', 'duỡ', 'đuơ', 'duợ',
                    'đuờ', 'duơ', 'đùo',
                   'đưò',  'dùõ',  'đưọ', 'đưo','đuo']
__tones_ignore__+=['iừo',  'iuờ', 'iuo', 'iưò' 'iúo','độe','uừ','ưè','ưè','ye']

__tones_ignore__+=['iúo']

__tones_ignore__+=['dựạ', 'dưà','dựá']
__tones_ignore__+=['đẩo',  'đãó', 'đạọ','daở', 'đàọ','đậo']
__tones_ignore__+=['đâù', 'dâú','đâụ',  'đaư', 'đâú',
                   'dâù']
__tones_ignore__+=['ỉeu', 'iềú', 'ìeu', 'iêù', 'iêũ', 'iêụ', 'iểù', 'iềụ', 'iếú', 'iêú', 'iềủ', 'iềù','yêú']
__tones_ignore__+=['àỳ', 'àý', 'âỵ', 'áý', 'âỷ',
                   'ẩý', 'âý', 'áỵ',
                   'ấý','âỳ',  'àỵ', 'ấỵ',  'ạỵ', 'ậỵ', 'âỹ']

__tones_ignore__+=['êú','êừ',  'eu', 'ếú', 'êù']
__tones_ignore__+=['àỳ', 'àý',  'âỵ', 'áý', 'âỷ', 'ẩý', 'âý', 'áỵ',
                   'ấý',  'âỳ', 'àỵ', 'ấỵ', 'ạỵ', 'ậỵ', 'âỹ']
__tones_ignore__+=['êú',  'êừ',  'ếú', 'êù']
__tones_ignore__+=['âú',  'âụ', 'âử', 'aư', 'âủ', 'âù', 'ậụ', 'àù', 'aủ',
                   'âũ',  'ầù', 'âư']
__tones_ignore__+=[ 'àô', 'ăộ', 'aở', 'áó', 'áọ', 'ạọ','aồ','àò', 'ảỏ', 'àọ', 'aỏ','aõ']
__tones_ignore__+=['ìo','ịo']
__tones_ignore__+=['ưô', 'ụo', 'ưọ', 'uó', 'ữõ', 'ưố','ưỏ', 'ưo',  'ưộ',
                    'ùo', 'ưò', 'ưồ', 'ụộ', 'ưổ','uư']
__tones_ignore__+=['ựạ', 'ưá', 'ưà', 'ưầ', 'ửả',
                   'ụậ', 'ưả', 'ửá',
                   'ưã', 'ưạ', 'ủạ', 'ữạ',
                    'ụá', 'ưă', 'ứá',
                    'ủả']
__tones_ignore__ +=[
                        'ôẩ', 'ôa', 'ọả', 'ớá', 'ồa',
                        'ơa', 'ọạ', 'óá', 'ôá','ốa',
                        'ổà', 'ởã', 'ốá', 'ơạ', 'ôă', 'ơả', 'òà','úý','ụỵ','ùỳ','ủỷ','ưy','ủỵ','ùỷ','uu','ữy','ịệ']
skip_tone_key =[
            "ad",
            "ada",
            "odi",
            "ayu",
            "ede",
            "yde",
            "ayi",
            "dd",
            "uyd","ado","oya","doo","eay","yd","yoo","uid","yea","dio","yi","yda","oda","yo","dei",
    "dii","yu","ady","iye","dee","dad","yed","ode","ddd","iyo","idi","iya","yy","oyi","aye",
    "udy","dyo","uoy","ud","aao","ayd","ade","yio","dda","dea","aya","ddo","yoe","ody","aod","ydy",
    "eid","oiy","eya","iad","uud","yia","idd","ded","odo","aey","aaa","edi","ooy","eoy","dya",
    "eyd","dae","aoy","yua","yye","udo","eye","yoy","ied","ydi","iyu","oey","yoa","oud","yeo","ddi",
    "uyy","ide","oed","yud","ido","yao","ydo","idu","aay","daa","ida","aiy","yuo","aai","uyi","iey",
    "uda","dou","adi","auy","yue","yoi","doy","uey","dde","yau","udu","ayy","eda","uuy","dey","yie","edu","ude",
    "adu",
    "duu","ayo","dye","odu","ii","ya","dy","iy","ey","oy","oo"
        ]


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
                if __config__.tones.get(x[0]) and x[0] not in __tones_ignore__:
                    __config__.tones.get(x[0]).append(v)
                elif __tones_ignore__:
                    if v not in __tones_ignore__:
                        __config__.tones[x[0]] = [v]
                lst.append(v)
                _fx[v] = x[0]

        __config__.tones = __load_data_from_zip__(os.path.join(source_dir, "vn_predictor_accents.npy.zip"),
                                                  dataset_path)

        if __tones_ignore__:
            tmp = collections.OrderedDict()
            set_of_ignore = set(__tones_ignore__)
            for k, v in __config__.tones.items():
                if len(k) <= 3 and  k not  in skip_tone_key:
                    if len(v)==1 and k==v[0]:
                        continue
                    if k[-1] in ['d','đ']:
                        continue
                    lst = list(set(v).difference(set_of_ignore))
                    if len(lst) > 0:
                        tmp[k] = lst
            del __config__.tones
            __config__.tones = tmp
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
    _l=[]
    for x in f_check:
        for y in f_check:
            for z in f_check:
                if __config__.tones.get(x + y+z):
                    _l+= __config__.tones.get(x + y+z)
                    if len(_l)>10:
                        _l =[]

    return __config__


def get_config():
    global __config__
    global __resource_loader_lock__
    if __config__ is None:
        __resource_loader_lock__.acquire()
        __get_config__()
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
