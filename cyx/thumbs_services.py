import os.path
import pathlib
import threading

import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.common import config
__version__ = "0.5"
import webp
from PIL import Image
class ThumbService:
    def __init__(
            self,
            memcache_services=cy_kit.singleton(MemcacheServices),
            mongodb_service=cy_kit.singleton(MongodbService),
    ):
        self.memcache_services: MemcacheServices = memcache_services
        self.cache_group = f"/{__version__}/{config.file_storage_path}/{__file__}/{type(self).__name__}/thumb"
        self.mongodb_service = mongodb_service


    def get_thumb_type(self, ext_file) -> str:
        if ext_file.lower() in config.ext_office_file:
            return "office"
        else:
            import mimetypes
            mt, _ = mimetypes.guess_type(f"x.{ext_file}")
            if mt.startswith("image/") or ext_file == "avif":
                return "image"
            if mt.startswith("video/"):
                return "video"
        return ext_file

    async def get_async(self, app_name: str, directory: str, size: int):
        cache_key = f"{self.cache_group}/{app_name}/{directory}".replace(" ","_")
        ret = self.memcache_services.get_str(cache_key)

        if ret == "":
            return None
        if ret is not None and os.path.isfile(ret):
            if os.stat(ret).st_size==0:
                os.remove(ret)
                self.memcache_services.remove(cache_key)
                ret=None
        if ret is not None and not os.path.isfile(ret):
            self.memcache_services.remove(cache_key)
            ret = None
        if ret is None:
            upload_id = directory.split('/')[0]
            doc_context = self.mongodb_service.db(app_name).get_document_context(DocUploadRegister)
            upload = await doc_context.context.find_one_async(
                doc_context.fields.id == upload_id
            )
            if not upload or upload[doc_context.fields.Status] == 0:
                return None

            main_file_id = upload[doc_context.fields.MainFileId]

            if isinstance(main_file_id, str) and "://" in main_file_id:
                real_file_path = os.path.join(config.file_storage_path, main_file_id.split("://")[1])
                real_dir_path = pathlib.Path(real_file_path).parent.__str__()
                if os.path.isdir(real_dir_path):
                    ext_file = upload[doc_context.fields.FileExt]
                    if ext_file is None:
                        ext_file = pathlib.Path(real_file_path).suffix
                        if ext_file != "":
                            ext_file = ext_file[1:]
                        else:
                            self.memcache_services.set_str(cache_key, "")
                            return None

                    thumb_type = self.get_thumb_type(ext_file)
                    if thumb_type == "office":
                        return None
                    elif thumb_type == "image":
                        thumb_file_path = self.get_thumb_path_from_image(
                            in_path=real_dir_path,
                            size=size,
                            main_file_path=real_file_path
                        )
                        self.memcache_services.set_str(cache_key, thumb_file_path)
                        return thumb_file_path
                    elif thumb_type=="video":
                        return None
                    else:
                        return None

        return ret
    def get_thumb_path_from_image(self, in_path, size, main_file_path):
        """Scales an image while maintaining its aspect ratio.

                Args:
                    image_path (str): Path to the image file.
                    new_width (int, optional): Desired width of the scaled image.
                    new_height (int, optional): Desired height of the scaled image.

                Returns:
                    Image: The scaled image.
                """

        ret_image_path = os.path.join(pathlib.Path(main_file_path).parent.__str__(), f"{size}.webp")
        with Image.open(main_file_path) as img:
            original_width, original_height = img.size
            if size > max(original_width, original_height):
                size = int(max(original_width, original_height))
            rate = size / original_width
            w, h = size, int(original_height * rate)
            if original_height > original_width:
                rate = size / original_height
                w, h = int(original_width * rate), size
            scaled_img = img.resize((w, h))  # High-quality resampling
            webp.save_image(scaled_img, ret_image_path, lossless=True)  # Set lossless=False for lossy compression

            return ret_image_path

    async def get_customize_async(self, app_name, directory):
        cache_key = f"{self.cache_group}/{app_name}/{directory}/get_customize_async".replace(" ", "_")
        ret = self.memcache_services.get_str(cache_key)
        if isinstance(ret,str) and os.path.isfile(ret):
            return ret
        name_only = pathlib.Path(directory).stem
        if name_only.isnumeric():
            return await self.get_async(
                app_name=app_name,
                directory=directory,
                size=int(name_only)
            )
        else:
            return await self.get_async(
                app_name=app_name,
                directory=directory,
                size=700
            )

