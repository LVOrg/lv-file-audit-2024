"""
Document layout analysis require a lot of settings at Operating System before it started
This package provides some functions to run at the end-point of thou's application.

Note!!!!!!:All functions in this package must be called at the most top of thou's application
Lưu ý!!!!!!: Tất cả các chức năng trong gói này phải được gọi ở đầu ứng dụng của bạn
-----------------------
Document layout analysis yêu cầu nhiều cài đặt tại Hệ điều hành trước khi bắt đầu
Gói này cung cấp một số chức năng để chạy ở end-point của ứng dụng của bạn.
Example :
import docment_layout_analysis
docment_layout_analysis.set_offline_dataset(true) # the dataset of AI is already in thou's OS
                                                  # OS needn't dowlnoad it from dataset hub
... any thou's source code star from here
if __name__=="__main__":
.....

"""


import os
import pathlib
__path_to_this_package__ = pathlib.Path(__file__).parent.__str__()

import shutil
import string
import subprocess
import sys
# import gradio
__tesseract_path__ = shutil.which("tesseract")
__tesseract_languages__ = None

import typing

"""
The package is require tesseract
Yêu cầu tesseract

"""
if __tesseract_path__ is None:
    """
    If thou's OS did not have "tesseract", we will cause the problem here
    Nếu hệ điều hành của bạn không có "tesseract", chúng tôi sẽ gây ra sự cố tại đây
    """
    raise Exception(f"tesseract was not found in thou's OS \n"
                    f"Install before run this pacage")
__ocr_languages__ = ["eng","vie"]
__working_path__ = pathlib.Path(__file__).parent.parent.parent.__str__()
sys.path.append(__working_path__)
__full_path_to_data_set__ = os.path.abspath(os.path.join(__working_path__,"dataset"))
"""
The path to root directory of applcation
"""


def set_offline_dataset(is_offline: bool):
    """
    Set offline mode or online mode \n
    For offline mode: The system assume that: all necessary dataset is in thou's OS \n
    For online mode: Dataset synchronize  is always start whenever thou's application start \n
    --------------------------------------------------------------\n
    Đặt chế độ ngoại tuyến hoặc chế độ trực tuyến \n
    Đối với chế độ ngoại tuyến: Hệ thống giả định rằng: tất cả tập dữ liệu cần thiết đều có trong hệ điều hành của bạn \n
    Đối với chế độ trực tuyến: Đồng bộ hóa tập dữ liệu luôn bắt đầu bất cứ khi nào ứng dụng của bạn bắt đầu \n
    -------------------------------------- \n
    Note: this method was always called at the most-top of thou's application \n
    Lưu ý: Method này luôn được gọi ở đầu ứng dụng của bạn

    :param is_offline:
    :return:
    """
    if is_offline:
        os.environ["TRANSFORMERS_OFFLINE"] = "true"
        os.environ["HF_HUB_OFFLINE"] = "true"

    else:
        os.environ["TRANSFORMERS_OFFLINE"] = "false"
        os.environ["HF_HUB_OFFLINE"] = "false"


def set_dataset_path(abs_or_relative_path: str):
    """
    AI or deep-learning framework required dataset in thou's application. \n
    In the most case, the dataset will get from somewhere in dataset-hub on Internet and reuse on the next time. \n
    The method will tell Document layout analysis that dataset locates at "abs_or_relative_path" \n
    if "abs_or_relative_path" start with "./" . That means "abs_or_relative_path" is relative path from "__working_path__" \n
    The other case is always absolute path in thou's OS \n
    ----------------------------------------------------- \n
    Bộ dữ liệu yêu cầu AI hoặc khung học sâu trong ứng dụng của bạn. \n
    Trong hầu hết các trường hợp, tập dữ liệu sẽ lấy từ một nơi nào đó trong trung tâm tập dữ liệu trên Internet và sử dụng lại vào lần tiếp theo.\n
    Phương pháp này sẽ báo cáo phân tích bố cục Tài liệu rằng tập dữ liệu nằm ở "abs_or_relative_path" \n
    nếu "abs_or_relative_path" bắt đầu bằng "./" . Điều đó có nghĩa là "abs_or_relative_path" là đường dẫn tương đối từ "__working_path__" \n
    Trường hợp khác luôn là đường dẫn tuyệt đối trong hệ điều hành của bạn \n
    :param abs_or_relative_path:
    :return:
    """
    global __working_path__
    global __path_to_this_package__

    full_path_to_data_set = abs_or_relative_path
    if abs_or_relative_path[0:2] == "./":
        """
        if start with "./" -> relative path
        """
        full_path_to_data_set = os.path.abspath(
            os.path.join(__working_path__, abs_or_relative_path[2:])
        )
    dd_one_path_source = os.path.abspath(
        os.path.join(__path_to_this_package__, "conf_dd_one.yaml")
    )
    dd_one_path_dest = os.path.abspath(
        os.path.join(full_path_to_data_set, "conf_dd_one.yaml")
    )
    if not os.path.isdir(pathlib.Path(dd_one_path_dest).parent.__str__()):
        os.makedirs(pathlib.Path(dd_one_path_dest).parent.__str__(),exist_ok=True)
    if not os.path.isdir(dd_one_path_dest):
        shutil.copy(dd_one_path_source,dd_one_path_dest)
    doctr_path = os.path.abspath(
        os.path.join(full_path_to_data_set, "doctr")
    )
    if not os.path.isdir(doctr_path):
        """
        if not exist "doctr_path" create it
        """
        os.makedirs(doctr_path, exist_ok=True)
    # raise Exception(full_path_to_data_set)
    os.environ["XDG_CACHE_HOME"] = full_path_to_data_set


    os.environ["DOCTR_CACHE_DIR"] = doctr_path
    global __full_path_to_data_set__
    __full_path_to_data_set__ = full_path_to_data_set
    print(f"Thou's system will with dataset locate at:\n'{full_path_to_data_set}'")
def get_dataset_path():
    global __full_path_to_data_set__
    return __full_path_to_data_set__

def is_tesseract_available() -> bool:
    global __working_path__
    return __tesseract_path__ is not None


def get_tesseract_version():
    import subprocess
    import os
    """
    get tesseract version
    """
    global __working_path__
    try:
        output = subprocess.check_output(
            [__tesseract_path__, "--version"],
            stderr=subprocess.STDOUT,
            env=os.environ,
            stdin=subprocess.DEVNULL,
        )
    except OSError:
        raise Exception(f"tesseract was not found in thou's OS")
    except Exception:
        cmd="find / -name tessdata"
        output = subprocess.check_output(
            cmd.split(' '),
            stderr=subprocess.STDOUT,
            env=os.environ,
            stdin=subprocess.DEVNULL,
        )
        raw_version = output.decode("utf-8").rstrip('\n').rstrip('\n')
        raw_version =raw_version.split('/')
        return raw_version[len(raw_version)-2]
    raw_version = output.decode("utf-8")
    str_version, *_ = raw_version.lstrip(string.printable[10:]).partition(" ")
    str_version, *_ = str_version.partition("-")
    return str_version

def get_tessract_data_path()->str:
    import subprocess
    import os
    output = subprocess.check_output(
        ["find","/usr","-name","tessdata"],
        stderr=subprocess.STDOUT,
        env=os.environ,
        stdin=subprocess.DEVNULL,
    )
    txt_output = output.decode("utf-8").lstrip('\n').split('\n')[0].rstrip('\n')
    return txt_output
def get_tesseract_languages():
    """
    get tesseract languages
    :return:
    """
    import subprocess
    import os
    import pathlib
    global __tesseract_languages__
    if __tesseract_languages__ is None:
        try:
            output = subprocess.check_output(
                [__tesseract_path__, "--list-langs"],
                stderr=subprocess.STDOUT,
                env=os.environ,
                stdin=subprocess.DEVNULL,
            )
            txt_output = output.decode("utf-8")
            __tesseract_languages__ = txt_output.split(':')[1].lstrip('\n').rstrip('\n').split('\n')
        except Exception:
            tess_path= get_tessract_data_path()
            output = subprocess.check_output(
                ["find",tess_path,"-name", "*.traineddata"],
                stderr=subprocess.STDOUT,
                env=os.environ,
                stdin=subprocess.DEVNULL,
            )
            txt_output = output.decode("utf-8")
            __tesseract_languages__ = txt_output.split('\n')
            __tesseract_languages__ = [pathlib.Path(x).stem for x in __tesseract_languages__ if len(x)>0]
            return __tesseract_languages__
    return __tesseract_languages__


def set_tesseract_path(abs_path):
    import pytesseract
    pytesseract.get_languages()


__message__ = f"Tesseract is in thou's OS with below information:\n" \
              f"Path='{__tesseract_path__}'\n" \
              f"Version:{get_tesseract_version()}\"" \
              f"Languages:\t\n" + '\t\n-'.join(get_tesseract_languages())
print(__message__)


def set_languages(*args,**kwargs):
    global __ocr_languages__
    if isinstance(args,tuple):
        __ocr_languages__ = list(args)
    if isinstance(args,str):
        __ocr_languages__ = [args]
    print(f"Thou's system now is running with {','.join(__ocr_languages__)}")


def get_languages():
    """
    Get languages was set by "set_languages" or default
    :return:
    """
    global __ocr_languages__
    return __ocr_languages__


