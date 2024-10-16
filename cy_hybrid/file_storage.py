class HybridFileService:
    from cyx.common.base import T

    from typing import List

    from cyx.common.file_storage_mongodb import MongoDbFileReader

    def create_async(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
                     size) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def create(self, app_name: str, rel_file_path: str, content_type: str, chunk_size: int,
               size: int) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def db_name(self, app_name: str):
        """
        somehow to implement thy source here ...
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

    def get_file_async(self, app_name: str, file_id):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def delete_files_by_id(self, app_name: str, ids: List, run_in_thread: bool):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_info_by_id(self, app_name, id):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def db(self, app_name: str):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

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

    def delete_files(self, app_name, files: List, run_in_thread: bool):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_id(self, app_name: str, id: str) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_name_async(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_id_async(self, app_name: str, id: str) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def store_file(self, app_name: str, source_file: str, rel_file_store_path: str) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_file_by_name(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def expr(self, cls: T) -> T:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_reader_of_file(self, app_name: str, from_chunk, id) -> MongoDbFileReader:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented