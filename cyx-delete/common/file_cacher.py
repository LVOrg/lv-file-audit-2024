import os

import cy_kit
from cyx.common.share_storage import ShareStorageService


class FileCacherService:
    """
    FileCache manager
    """
    def __init__(self, share_storage_service: ShareStorageService = cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service
        self.__cache_dir__ = os.path.join(self.share_storage_service.get_root(),"cache")
        if not os.path.isdir(self.__cache_dir__):
            os.makedirs(self.__cache_dir__, exist_ok=True)
        self.__cache__ = {}

    def get_path(self, relative_path:str):
        if self.__cache__.get(relative_path) is None:
            self.__cache__[relative_path] =os.path.abspath(os.path.join(self.__cache_dir__,relative_path))
            if not os.path.isdir(self.__cache__[relative_path]):
                os.makedirs(self.__cache__[relative_path],exist_ok=True)
        return self.__cache__[relative_path]
