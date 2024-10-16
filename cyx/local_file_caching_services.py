"""
This source code 100 percent generated by Gemini
"""
import gc
import os
import hashlib
import pathlib
import shutil

import cy_file_cryptor.context
from cyx.common import config
cy_file_cryptor.context.set_server_cache(config.cache_server)
class LocalFileCachingService:
    """
    Provides methods for caching files from an NFS server to a local directory.

    Attributes:
        cache_directory (str): The local directory to store cached files.
        limit_cache_size_gb (int): The maximum size of the cache in gigabytes.
    """

    def __init__(self):
        """
        Initializes a LocalFileCachingService object.


        """

        self.cache_directory = os.path.join(pathlib.Path(__file__).parent.parent.__str__(),"tem-caching")
        self.limit_cache_size_gb = 2
        self.hashing_cache = {}

        os.makedirs(self.cache_directory, exist_ok=True)  # Create cache directory if needed

    def clear_cache_by_upload_id(self,upload_id):
        remove_items = []
        for k,v in self.hashing_cache.items():
            id = pathlib.Path(k).parent.name
            if id== upload_id:
                remove_items+=k
        for x in remove_items:
            if os.path.isfile(x):
                os.remove(x)
            if self.hashing_cache.get(x):
                del self.hashing_cache[x]
        gc.collect()
    def cache_file(self, server_file_path):
        """
        Caches a file from an NFS server to the local cache directory, managing cache size limits.

        Args:
            server_file_path (str): The full path to the file on the NFS server.

        Returns:
            str: The full path of the cached file, or None if caching failed.

        Raises:
            OSError: If there are issues accessing or creating files/directories.
        """

        cached_file_path = self.hashing_cache.get(server_file_path)
        if not cached_file_path or not os.path.isfile(cached_file_path):
            file_hash = hashlib.sha256(server_file_path.encode()).hexdigest()
            file_extension = os.path.splitext(server_file_path)[1]
            cached_file_path = os.path.join(self.cache_directory, f"{file_hash}{file_extension}")
            self.hashing_cache[server_file_path] = cached_file_path

        if os.path.isfile(cached_file_path):
            return cached_file_path
        # Ensure sufficient cache space, deleting oldest files if needed
        while True:
            available_space = self.get_available_space_gb()
            if available_space >= self.get_file_size_gb(server_file_path):
                break

            try:
                oldest_file = self.find_oldest_file()
                if self.hashing_cache.get(oldest_file):
                    del self.hashing_cache[oldest_file]
                    gc.collect()
                if os.path.isfile(oldest_file):
                    os.remove(oldest_file)

            except OSError as err:
                raise OSError(f"Failed to manage cache space: {err}")

        try:

            with open(server_file_path,"rb") as fs:
                with open(cached_file_path,"wb") as fc:
                    fc.write(fs.read())

            return cached_file_path
        except OSError as err:
            raise OSError(f"Failed to copy file: {err}")

    # Helper functions for clarity (implementations depend on language/libraries used)
    def get_available_space_gb(self):
        """
        Gets the available disk space in gigabytes for the cache directory.

        Returns:
            float: The available space in gigabytes, or None on error.
        """

        try:
            stat = os.statvfs(self.cache_directory)
            free_bytes = stat.f_bsize * stat.f_bfree
            return free_bytes / (1024 ** 3)  # Convert bytes to gigabytes
        except OSError:
            return None

    def get_file_size_gb(self, file_path):
        """
        Gets the size of a file in gigabytes.

        Args:
            file_path (str): The full path to the file.

        Returns:
            float: The size of the file in gigabytes, or None on error.
        """

        try:
            stat = os.stat(file_path)
            file_size_bytes = stat.st_size
            return file_size_bytes / (1024 ** 3)  # Convert bytes to gigabytes
        except OSError:
            return None

    def find_oldest_file(self):
        """
        Finds the oldest file in the cache directory.

        Returns:
            str: The full path of the oldest file, or None if the directory is empty.
        """

        cache_dir = pathlib.Path(self.cache_directory)

        if not cache_dir.exists() or not any(cache_dir.iterdir()):
            return None  # Directory doesn't exist or is empty

        oldest_file = min(cache_dir.iterdir(), key=os.path.getmtime)
        return str(oldest_file)