import typing

import cy_kit


class FileStorageObject:
    @classmethod
    def get_size(cls) -> int:
        pass

    @classmethod
    def seek(cls, position:int):
        pass

    @classmethod
    def tell(cls)->int:
        pass

    @classmethod
    def read(cls, size:int=None)->bytes:
        pass

    @classmethod
    def push(cls,content:bytes, chunk_index:int):
        pass

    @classmethod
    async def push_async(cls, content: bytes, chunk_index: int):
        pass
    @classmethod
    def get_id(cls)->str:
        pass

    @classmethod
    async def get_id_async(cls) -> str:
        pass
    def close(self):
        pass







class FileStorageService_delete:

    def get_file_by_name(self, app_name, rel_file_path: str) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented
    async def get_file_by_name_async(self, app_name, rel_file_path: str) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented
    def copy(self, app_name: str, rel_file_path_from: str, rel_file_path_to, run_in_thread: bool) -> FileStorageObject:
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
                   run_in_thread: bool) -> FileStorageObject:
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

    def get_file_by_id(self, app_name: str, id: str) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented
    def get_file_by_id_async(self, app_name: str, id: str) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented
    def create(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
               size) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented
    async def create_async(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
               size) -> FileStorageObject:
        """
        some how to implement thy source here ...
        """
        raise NotImplemented

    def delete_files_by_id(self, app_name: str, ids: typing.List[str], run_in_thread: bool):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented
