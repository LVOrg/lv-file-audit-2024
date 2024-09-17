"""
This file is declare a lib manage temp directories and file for background processing

"""
from cyx.common import config
class TempFileService:
    """
    This class is used to manage temp directories and file for background processing
    """
    def __init__(self):
        self.__file_storage_path__ = config.file_storage_path
    @property
    def file_storage_path(self):
        """
        This property is used to get the file storage path
        """
        return self.__file_storage_path__


