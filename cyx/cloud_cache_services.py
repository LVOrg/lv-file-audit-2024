import os.path
import threading
import traceback
import typing

import requests

import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
class CloudCacheInfo:
    app_name: str
    directory: str
    storage_type: str
    cloud_id: str
    content_type:str
    upload_id:str
    file_name: str

class CloudCacheService:
    def __init__(self, memcache_services:MemcacheServices= cy_kit.singleton(MemcacheServices)):
        self.memcache_services=memcache_services
        self.cache_dir = os.path.join("/var","www","cache")
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir,exist_ok=True)
        self.prefix_cache_key = f"{type(self).__module__}/{type(self).__name__}"


    def cache_content(self,app_name:str, upload_id:str,cloud_id:str, url:str, header:dict):
        """

        :param app_name:
        :param upload_id:
        :param cloud_id:
        :param url:
        :param header:
        :return:
        """
        def run():
            try:
                url_download = url
                headers = header
                download_file_path = os.path.join(self.cache_dir,upload_id)
                response = requests.get(url_download,headers=headers)
                if not response.status_code == 200:
                    print(f"Failed to get file size for {url_download}")
                    return None

                file_size = int(response.headers.get('Content-Length', 0))
                if file_size+self.get_used_space()>(1024**3)*2:
                    self.clear_cache(file_size)
                self.do_download(download_to=download_file_path,response=response)
                self.memcache_services.set_str(f"{self.prefix_cache_key}/{upload_id}",download_file_path)
            except:
                print(traceback.format_exc())
        threading.Thread(target=run).start()

    def clear_cache(self, file_size:int):
        """
        delete the oldest file in cache_dir utils enough to store file with size embody by file_size
        :param file_size:  file_size in bytes
        :return:
        """
        target_free_space = file_size
        freed_space = 0

        # Get list of files in the cache directory
        files = [os.path.join(self.cache_dir, f) for f in os.listdir(self.cache_dir)]

        # Sort files by modification time (oldest first)
        files.sort(key=lambda f: os.path.getmtime(f))

        # Delete files until enough space is freed up
        for file in files:
            try:
                file_stats = os.stat(file)
                file_size = file_stats.st_size
                if freed_space + file_size >= target_free_space:
                    break  # Reached target free space
                os.remove(file)
                freed_space += file_size
                print(f"Deleted old file: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

        # Log if target space wasn't reached
        if freed_space < target_free_space:
            print(f"Warning: Couldn't free up enough space ({freed_space} bytes) in cache directory.")

    def get_used_space(self):
        stat = os.statvfs(self.cache_dir)
        return stat.f_blocks * stat.f_bsize

    def do_download(self, download_to, response):
        """Downloads a file from a URL and saves it to the specified location.

          Args:
            download_to: Path to save the downloaded file.
            url: URL of the file to download.
            headers: Optional dictionary of headers for the download request.

          Returns:
            True if download is successful, False otherwise.
          """

        with open(download_to, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

    def get_from_cache(self, upload_id):
        ret = self.memcache_services.get_str(f"{self.prefix_cache_key}/{upload_id}")
        if not isinstance(ret,str):
            download_file_path = os.path.join(self.cache_dir, upload_id)
            if os.path.isfile(download_file_path):
                self.memcache_services.set_str(f"{self.prefix_cache_key}/{upload_id}",download_file_path)
                return download_file_path
            else:
                return None
        else:
            if not os.path.isfile(ret):
                self.memcache_services.delete_key(f"{self.prefix_cache_key}/{upload_id}")
                return None
            return  ret

    def cache_request(self,
                      app_name:str,
                      directory:str,
                      storage_type:str,
                      cloud_id:str,
                      content_type:str,
                      upload_id:str,
                      file_name:str):
        key = f"{self.prefix_cache_key}/{app_name}/{directory}"
        data_cache= CloudCacheInfo()
        data_cache.cloud_id=cloud_id
        data_cache.storage_type=storage_type
        data_cache.app_name=app_name
        data_cache.directory=directory
        data_cache.content_type = content_type
        data_cache.upload_id=upload_id
        data_cache.file_name =file_name

        self.memcache_services.set_object(key,data_cache)

    def get_request_from_cache(self, app_name, directory)->typing.Optional[CloudCacheInfo]:
        key = f"{self.prefix_cache_key}/{app_name}/{directory}"
        ret = self.memcache_services.get_object(key,CloudCacheInfo)
        if ret:
            return ret
        else:
            return None






