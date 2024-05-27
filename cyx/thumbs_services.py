import json
import os.path
import pathlib
import threading

import cy_kit
import cyx.common.msg
from cyx.cache_service.memcache_service import MemcacheServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.common import config
from cyx.remote_caller import RemoteCallerService
__version__ = "0.5"
from functools import cache
import hashlib

from cyx.common.rabitmq_message import RabitmqMsg
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
class ThumbService:
    def __init__(
            self,
            memcache_services=cy_kit.singleton(MemcacheServices),
            mongodb_service=cy_kit.singleton(MongodbService),
            msg=cy_kit.singleton(RabitmqMsg),
            local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService),
            remote_caller_service:RemoteCallerService = cy_kit.singleton(RemoteCallerService)
    ):
        self.memcache_services: MemcacheServices = memcache_services
        self.cache_group = f"/{__version__}/{config.file_storage_path}/{__file__}/{type(self).__name__}/thumb"
        self.mongodb_service = mongodb_service
        self.msg = msg
        self.local_api_service=local_api_service
        self.remote_caller_service=remote_caller_service

    def get_thumb_type(self, ext_file) -> str:
        if ext_file.lower() == "pdf":
            return "pdf"
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
        key = self.get_cache_key(app_name=app_name,directory=directory,size=size)
        ret= self.memcache_services.get_str(key)
        # if ret:
        #     return ret


        upload_id = directory.split('/')[0]
        upload_item = await Repository.files.app(app_name).context.find_one_async(
            Repository.files.fields.Id==upload_id
        )
        server_file, rel_file_path, download_file_path, token, local_share_id = self.local_api_service.get_download_path(
            upload_item=upload_item,
            app_name=app_name
        )
        file_type = self.get_thumb_type(pathlib.Path(rel_file_path).suffix.lstrip("."))
        abs_file_path = os.path.join("/mnt/files",rel_file_path)
        folder_dir = pathlib.Path(abs_file_path).parent.__str__()
        thumb_file = os.path.join(folder_dir,f"{size}.webp")

        if os.path.isfile(thumb_file):
            self.memcache_services.set_str(key,thumb_file)
            return thumb_file
        image_file = abs_file_path
        if file_type !="image":
            image_file=f"{abs_file_path}.png"
        if os.path.isfile(image_file):
            ret = self.do_scale_size(file_path=image_file,size=size)
            self.memcache_services.set_str(key, ret)
            return ret
        else:

            if file_type=="office":
                data = self.remote_caller_service.get_image_from_office(
                    url=f"{config.remote_office}//image-from-office-from-share-file",
                    local_file=abs_file_path,
                    remote_file=server_file,
                    memcache_server = config.cache_server
                )
                if data.get("image_file"):
                    office_image_file=data.get("image_file")

                    from cy_file_cryptor.context        import create_encrypt
                    with create_encrypt(f"{abs_file_path}.png"):
                        with open(f"{abs_file_path}.png","wb") as fw:
                            with open(office_image_file,"rb") as fr:
                                data_read = fr.read(1024)
                                while data_read:
                                    fw.write(data_read)
                                    del data_read
                                    data_read = fr.read(1024)

                    os.remove(office_image_file)
                    ret = self.do_scale_size(file_path=f"{abs_file_path}.png", size=size)
                    self.memcache_services.set_str(key, ret)
                    return ret



                print(data)

            print(file_type)
        # print(folder_dir)
        # if os.path.isfile(abs_file_path):
        #     print(abs_file_path)

        return None
    async def get_async_delete(self, app_name: str, directory: str, size: int):

        upload_id= directory.split('/')[0]
        cache_key = f"{self.cache_group}/{app_name}/{upload_id}/get_async"
        ret = self.memcache_services.get_str(cache_key)

        if ret == "":
            return None
        if ret is not None and os.path.isfile(ret):
            if os.stat(ret).st_size == 0:
                os.remove(ret)
                self.memcache_services.remove(cache_key)
                ret = None
        if ret is not None and not os.path.isfile(ret):
            self.memcache_services.remove(cache_key)
            ret = None
        if ret is None or not os.path.isfile(directory):
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
                thumn_file = os.path.join(real_dir_path,f"{size}.webp")
                if os.path.isfile(thumn_file):
                    self.memcache_services.set_str(cache_key,thumn_file)
                    return thumn_file
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


                    if thumb_type == "image":
                        if upload.get("ThumbnailsAble") == False:
                            return None
                        thumb_file_path = self.get_thumb_path_from_image(
                            in_path=real_dir_path,
                            size=size,
                            main_file_path=real_file_path
                        )
                        self.memcache_services.set_str(cache_key, thumb_file_path)
                        return thumb_file_path
                    elif os.path.isfile(f"{real_file_path}.png"):
                        thumb_file_path = self.get_thumb_path_from_image(
                            in_path=f"{real_file_path}.png",
                            size=size,
                            main_file_path=f"{real_file_path}.png"
                        )
                        return thumb_file_path
                    else:
                        self.msg.emit(
                            app_name=app_name,
                            data=upload,
                            message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE,
                            resource=real_file_path
                        )
                        return None
        return ret

    # def get_thumb_path_from_image(self, in_path, size, main_file_path):
    #     process_services_host = config.process_services_host or "http://localhost"
    #     try:
    #         txt_json = json.dumps(dict(
    #             in_path=in_path,
    #             size=size,
    #             main_file_path=main_file_path,
    #             mem_cache_server = config.cache_server
    #         ))
    #         client = Client(f"{process_services_host}:1114/")
    #         _, result = client.predict(
    #             txt_json,
    #             False,
    #             api_name="/predict"
    #         )
    #     except Exception as ex:
    #         print(ex)
    #     print(in_path,size,main_file_path)
    #     ret = os.path.join(pathlib.Path(in_path).parent.__str__(),f"{size}.webp")
    #     if os.path.isfile(ret):
    #         return ret


        return


    async def get_customize_async(self, app_name, directory):
        cache_key = f"{self.cache_group}/{app_name}/{directory}/get_customize_async".replace(" ", "_")
        ret = self.memcache_services.get_str(cache_key)
        if isinstance(ret, str) and os.path.isfile(ret):
            return ret
        name_only = pathlib.Path(directory).stem
        if name_only.isnumeric():
            ret = await self.get_async(
                app_name=app_name,
                directory=directory,
                size=int(name_only)
            )
            self.memcache_services.set_str(cache_key,ret)
            return ret
        else:
            return await self.get_async(
                app_name=app_name,
                directory=directory,
                size=700
            )
    @cache
    def get_cache_key(self, app_name, directory,size):
        """
        Create hash content 256 of app_name and directory
        :param app_name:
        :param directory:
        :return:
        """
        key_content =f"{type(self).__module__}/{type(self).__name__}/{app_name}/{directory}/{size}".lower()
        hashed_key = hashlib.sha256(key_content.encode('utf-8')).hexdigest()
        return hashed_key

    def do_scale_size(self, file_path, size):
        """
        Create scale size of image in file_path in size of square size ex: size=120 square is 120x120
        The scale file name is in format {size}.webp an place at the same folder of file_path
        :param file_path:
        :param size:
        :return:
        """
        import webp
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        ret_image_path = os.path.join(pathlib.Path(file_path).parent.__str__(), f"{size}.webp")
        temp_ret_image_path = os.path.join(pathlib.Path(file_path).parent.__str__(), f"{size}_tmp.webp")
        with Image.open(file_path) as img:
            original_width, original_height = img.size
            if size > max(original_width, original_height):
                size = int(max(original_width, original_height))
            rate = size / original_width
            w, h = size, int(original_height * rate)
            if original_height > original_width:
                rate = size / original_height
                w, h = int(original_width * rate), size
            scaled_img = img.resize((w, h))  # High-quality resampling

            from cy_file_cryptor.context import create_encrypt
            with create_encrypt(ret_image_path):
                webp.save_image(scaled_img, ret_image_path,
                                lossless=True)  # Set lossless=False for lossy compression

            return ret_image_path




