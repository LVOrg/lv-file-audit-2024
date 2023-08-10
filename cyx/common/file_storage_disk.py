import os.path
import pathlib
import typing

import cy_kit

from cyx.common.file_storage_mongodb import MongoDbFileStorage
@cy_kit.must_imlement(interface_class=MongoDbFileStorage)
class FileDiskStorage:
    def __init__(self,file_path:str, id:str):
        self.file_path =file_path.lower()
        self.id =id.lower()
        self._file =None

    @property
    def file(self):
        if self._file is None:
            self._file = open(self.file_path,"rb")
        return self._file

    def get_id(self) -> str:
        return self.id

    def get_size(self) -> int:
        """
        some how to implement thy source here ...
        """
        file_stats = os.stat(self.file_path)
        return file_stats.st_size

    def seek(self, position: int):
        """
        somehow to implement thy source here ...
        """
        return self.file.seek(position)

    def close(self):
        """
            somehow to implement thy source here ...
                """
        self.file.close()

    def push(self, content: bytes, chunk_index: int):
        """
        somehow to implement thy source here ...
        """
        if os.path.isfile(self.file_path):
            with open(self.file_path,"ab") as f:
                f.write(content)
        else:
            with open(self.file_path,"wb") as f:
                f.write(content)

    def tell(self) -> int:
        """
        somehow to implement thy source here ...
        """
        return self.file.tell()

    def read(self, size: int) -> bytes:
        """
        somehow to implement thy source here ...
        """
        return self.file.read(size)
import cyx.common
class FileDiskStorageService:
    def __init__(self):
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.config = cyx.common.config
        self.storage_path = self.config.storage_path
        if self.storage_path[0:2]=="./":
            self.storage_path=self.storage_path[2:]
            self.storage_path =os.path.abspath(os.path.join(self.working_dir,self.storage_path))
        if not os.path.isdir(self.storage_path):
            os.makedirs(self.storage_path,exist_ok=True)
    def get_file_by_name(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        """
        some how to implement thy source here ...
        """
        full_path = self.get_file_path(app_name, rel_file_path)

        return FileDiskStorage(file_path=full_path,id=rel_file_path)

    def copy(self, app_name: str, rel_file_path_from: str, rel_file_path_to, run_in_thread: bool) -> MongoDbFileStorage:
        """
                Copy file
                :param rel_file_path_to:
                :param rel_file_path_from:
                :param app_name:
                :param run_in_thread:True copy process will run in thread
                :return:
                        """
        raise NotImplemented

    def copy_by_id(self, app_name: str, file_id_to_copy: str, rel_file_path_to: str,
                   run_in_thread: bool) -> MongoDbFileStorage:
        """
                Copy file from id file and return new copy if successful
                :param app_name:
                :param file_id_to_copy:
                :param run_in_thread:
                :return:
                        """
        raise NotImplemented

    def delete_files(self, app_name, files: typing.List[str], run_in_thread: bool):
        """
        some how to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_id(self, app_name: str, id: str) -> FileDiskStorage:
        """
            some how to implement thy source here ...
        """

        full_path = self.get_file_path(app_name, id)

        return FileDiskStorage(file_path=full_path, id=id)

    def create(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
               size: int) -> FileDiskStorage:
        """
        somehow to implement thy source here ...
        """

        full_path = self.get_file_path(app_name, rel_file_path)

        return FileDiskStorage(file_path=full_path,id=rel_file_path)

    def get_file_path(self, app_name, rel_file_path):

        app_dir = os.path.join(self.storage_path, app_name)

        if not os.path.isdir(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        full_path = os.path.join(app_dir, rel_file_path.replace('/', os.sep))


        parent_dir = pathlib.Path(full_path).parent
        if not os.path.isdir(parent_dir.__str__()):
            os.makedirs(parent_dir.__str__(), exist_ok=True)
        return full_path

    def delete_files_by_id(self, app_name: str, ids: typing.List[str], run_in_thread: bool):
        """
        some how to implement thy source here ...
        """
        raise NotImplemented