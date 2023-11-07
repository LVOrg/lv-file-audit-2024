import datetime
import os.path
import pathlib

import cy_kit
from cy_xdoc.services.files import FileServices
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.common import config


class HybridFileStorage:
    def __init__(self,
                 file_storage_path: str,
                 app_name: str,
                 rel_file_path: str,
                 content_type: str,
                 chunk_size: int,
                 size: int,
                 file_services,
                 cacher):
        self.file_services: FileServices = file_services
        self.cacher: MemcacheServices = cacher
        self.file_storage_path = file_storage_path
        if not rel_file_path.startswith("local://"):
            self.id = self.__get_full_path_by_app_and_rel_path__(app_name, rel_file_path)
            if self.id is None:
                self.id = "@new_id"
            self.full_dir = os.path.join(
                self.file_storage_path, self.id
            )
            self.filename = os.path.split(rel_file_path)[1]
            self.full_path = os.path.join(self.full_dir, self.filename)
            if not os.path.isdir(self.full_dir):
                os.makedirs(self.full_dir, exist_ok=True)
            self.full_id = os.path.join(self.id, self.filename)
            if hasattr(config, "stream_buffering_size_in_KB") and isinstance(config.stream_buffering_size_in_KB, int):
                self.chunk_size = config.stream_buffering_size_in_KB
            else:
                print("Warning: stream_buffering_size_in_KB not found in config.yml, run default with 64KB")
                self.chunk_size = 1024 * 64
        else:
            self.id = rel_file_path[len("local://"):]
            self.full_id = self.id
            self.full_path = os.path.join(self.file_storage_path, self.full_id)
        if rel_file_path.startswith("thumbs/"):
            if not os.path.isfile(self.full_path):
                folder_path =pathlib.Path(self.full_path).parent.__str__()
                lst_files = list(os.listdir(folder_path))
                for filename in lst_files:
                    filepath = os.path.join(folder_path, filename)
                    if os.path.isfile(filepath) and filename.lower().endswith(f'_{self.filename}'):
                        self.full_path = filepath
                        break

            print("thumbnail_pyc dieu xe _2__60.webp")
        self.delegate = None

    def __is_uuid__(self, str_value):
        import re
        regex = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
        return regex.match(str_value) is not None

    def __get_full_path_by_app_and_rel_path__(self, app_name, rel_file_path) -> dict:
        key = f"HybridFileStorage/{app_name}/{rel_file_path}".replace(" ", "___")
        ret = self.cacher.get_str(key)
        if ret is None:
            id = rel_file_path.split('/')[0]
            if not self.__is_uuid__(id):
                id = rel_file_path.split('/')[1]
            upload = self.file_services.get_upload_register_with_cache(app_name, id)
            if upload is not None:
                register_on = upload.RegisterOn
                if isinstance(register_on, datetime.datetime):

                    doc_type = "unknown"
                    if hasattr(upload, "FileExt"):
                        doc_type = upload.FileExt[0:3]
                    ret = os.path.join(
                        app_name,
                        str(register_on.year),
                        f"{register_on.month:02}",
                        f"{register_on.day:02}",
                        doc_type,
                        id
                    )

                    self.cacher.set_str(key, ret)
            else:
                register_on = datetime.datetime.utcnow()
                doc_type = "unknown"

                if len(os.path.splitext(rel_file_path)) > 1:
                    doc_type = os.path.splitext(rel_file_path)[1][1:][0:3]
                ret = os.path.join(
                    app_name,
                    str(register_on.year),
                    f"{register_on.month:02}",
                    f"{register_on.day:02}",
                    doc_type,
                    id
                )

        return ret

    def seek(self, position):
        """
        somehow to implement thy source here ...
        """
        if self.delegate is None:
            self.__init_delegate__()
        return self.delegate.seek(position)

    async def read(self, size) -> bytes:
        """
        somehow to implement thy source here ...
        """

        if self.delegate is None:
            self.__init_delegate__()

        return self.delegate.read(size)

    def get_cursor(self, from_index, num_of_element, cursor):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented()

    def push(self, content: bytes, chunk_index):
        """
        somehow to implement thy source here ...
        """
        file_path = os.path.join(self.full_dir, self.filename)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(content)
        else:
            with open(file_path, "ab") as f:
                f.write(content)

    def get_id(self) -> str:
        """
        somehow to implement thy source here ...
        """
        return f"local://{self.full_id}"

    def push_async(self, content: bytes, chunk_index):
        """
        somehow to implement thy source here ...
        """
        return self.push(content, chunk_index)

    def tell(self):
        """
        somehow to implement thy source here ...
        """
        if self.delegate is None:
            self.__init_delegate__()
        return self.delegate.tell()

    def close(self):
        """
            some how to implement thy source here ...
                """
        if self.delegate is not None and hasattr(self.delegate, "close") and callable(self.delegate.close):
            self.delegate.close()

    def get_size(self):
        """
        somehow to implement thy source here ...
        """
        return os.path.getsize(self.full_path)

    async def get_id_async(self) -> str:
        """
        somehow to implement thy source here ...
        """
        return self.get_id()

    def cursor_len(self):
        raise NotImplemented()

    def __init_delegate__(self):
        import asyncio
        f = open(
            file=self.full_path,
            mode="rb"
        )

        self.delegate = f
