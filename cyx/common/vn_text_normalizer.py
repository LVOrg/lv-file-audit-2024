import os.path
import pathlib
__working_dir__ = pathlib.Path(__file__).parent.__str__()
import sys
sys.path.append(__working_dir__)
# def __bootstrap__():
#    global __bootstrap__, __loader__, __file__
#    import sys, pkg_resources, imp
#    print(os.path.join(__working_dir__,'VietnameseTextNormalizer.so'))
#    __file__ = pkg_resources.resource_filename(__name__,'VietnameseTextNormalizer.so')
#    __loader__ = None; del __bootstrap__, __loader__
#    imp.load_dynamic(__name__,__file__)
# __bootstrap__()
import VietnameseTextNormalizer
class VnTextNormalizer:
    def __init__(self):
        pass

    def correct(self,content:str):
        ret = VietnameseTextNormalizer.Normalize(content)
        return ret