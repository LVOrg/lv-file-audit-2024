import json
import mimetypes
import os.path
import pathlib
import threading
import time
import traceback

import bson.objectid
import cy_file_cryptor.context
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
import webp
from PIL import Image
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
from cyx.malloc_services import MallocService
from cyx.common.brokers import Broker
from cyx.common import msg
from cyx.file_utils_services import FileUtilService

class ThumbService:
    memcache_services = cy_kit.singleton(MemcacheServices)
    mongodb_service = cy_kit.singleton(MongodbService)
    msg = cy_kit.singleton(RabitmqMsg)
    local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService)
    remote_caller_service: RemoteCallerService = cy_kit.singleton(RemoteCallerService)
    malloc_service = cy_kit.singleton(MallocService)
    cache_group = f"/v03/{config.file_storage_path}/ThumbService/thumb"
    file_util_service = cy_kit.singleton(FileUtilService)
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
        if ret and os.path.isfile(ret):
            return ret


        upload_id = directory.split('/')[0]
        upload_item = await Repository.files.app(app_name).context.find_one_async(
            Repository.files.fields.Id==upload_id
        )

        if upload_item is None:

            return None

        real_file_path = await self.file_util_service.get_physical_path_async(
            app_name=app_name,
            upload_id=upload_id
        )
        mime_type, _ = mimetypes.guess_type(real_file_path)
        if mime_type.startswith("image/"):
            import PIL
            try:
                ret = self.do_scale_size(file_path=real_file_path, size=size)
                self.memcache_services.set_str(key, ret)
                return ret
            except PIL.UnidentifiedImageError:
                server_file, rel_file_path, download_file_path, token, local_share_id = self.local_api_service.get_download_path(
                    upload_item=upload_item,
                    app_name=app_name
                )
                file_ext = pathlib.Path(rel_file_path).suffix.lstrip(".")
                file_type = self.get_thumb_type(file_ext)

                self.run_generate_image(file_type=file_type,
                                        file_process=real_file_path,
                                        is_in_thred=True,
                                        app_name=app_name,
                                        upload_id=upload_id,
                                        size=size,
                                        cache_key=key,
                                        server_file=server_file,
                                        )
            except Exception as ex:
                return None
        if not upload_item.get("MainFileId") or  not isinstance(upload_item[Repository.files.fields.MainFileId],str) or not "://" in upload_item[Repository.files.fields.MainFileId]:
            """
            Recalculate file storage and location if upload's file is still in mongoDb
            """
            file_ext="unknown"
            if upload_item.get("FileExt"):
                file_ext = upload_item.get("FileExt").lower()[0:3]
            register_on = upload_item[Repository.files.fields.RegisterOn]
            rel_path =  f'{app_name}/{register_on.strftime("%Y/%m/%d")}/{file_ext}/{upload_id}/{upload_item[Repository.files.fields.FileName].lower()}'
            folder_path = os.path.join(config.file_storage_path, app_name,
                                       register_on.strftime("%Y/%m/%d").replace('/', os.sep),file_ext, upload_id)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, upload_item[Repository.files.fields.FileName].lower())
            import requests
            server_file = config.private_web_api +f"/api/{app_name}/file/{upload_item.id}/{upload_item[Repository.files.fields.FileName].lower()}"
            response = requests.get(server_file)
            if not os.path.isfile(file_path):
                """
                Checj angin. Why? For replication web deploy, may be another instance did it
                """
                if response.status_code == 200:
                    with cy_file_cryptor.context.create_encrypt(file_path):
                        with open(file_path, 'wb') as file:
                            file.write(response.content)
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.id==upload_id,
                        Repository.files.fields.MainFileId<<f"local://{rel_path}",
                        Repository.files.fields.StorageType << "local"
                    )
                    upload_item = await Repository.files.app(app_name).context.find_one_async(
                        Repository.files.fields.Id == upload_id
                    )
                else:
                    raise Exception(f"Can not donwload file {server_file}")
        server_file, rel_file_path, download_file_path, token, local_share_id = self.local_api_service.get_download_path(
            upload_item=upload_item,
            app_name=app_name
        )



        file_ext = pathlib.Path(rel_file_path).suffix.lstrip(".")
        file_type = self.get_thumb_type(file_ext)
        abs_file_path = os.path.join(config.file_storage_path, rel_file_path)


        folder_dir = pathlib.Path(abs_file_path).parent.__str__()
        thumb_file = os.path.join(folder_dir,f"{size}.webp")

        if os.path.isfile(thumb_file):
            self.memcache_services.set_str(key,thumb_file)
            return thumb_file
        image_file = abs_file_path
        if file_type !="image":
            image_file=f"{abs_file_path}.png"
        if os.path.isfile(image_file):
            import PIL
            try:
                ret = self.do_scale_size(file_path=image_file,size=size)
                self.memcache_services.set_str(key, ret)
                return ret
            except PIL.UnidentifiedImageError:
                if os.path.isfile(image_file):
                    os.remove(image_file)
                self.run_generate_image(file_type=file_type,
                                        file_process=abs_file_path,
                                        is_in_thred=True,
                                        app_name=app_name,
                                        upload_id=upload_id,
                                        size=size,
                                        cache_key=key,
                                        server_file=server_file,
                                        )
            except Exception as ex:
                print(image_file)
        else:
            self.run_generate_image(file_type=file_type,
                                    file_process=abs_file_path,
                                    is_in_thred=True,
                                    app_name=app_name,
                                    upload_id=upload_id,
                                    size=size,
                                    cache_key=key,
                                    server_file=server_file,
                                    )

        return None



    # async def get_customize_async(self, app_name, directory):
    #     cache_key = f"{self.cache_group}/{app_name}/{directory}/get_customize_async".replace(" ", "_")
    #     ret = self.memcache_services.get_str(cache_key)
    #     if isinstance(ret, str) and os.path.isfile(ret):
    #         return ret
    #     name_only = pathlib.Path(directory).stem
    #     if name_only.isnumeric():
    #         ret = await self.get_async(
    #             app_name=app_name,
    #             directory=directory,
    #             size=int(name_only)
    #         )
    #         self.memcache_services.set_str(cache_key,ret)
    #         return ret
    #     else:
    #         return await self.get_async(
    #             app_name=app_name,
    #             directory=directory,
    #             size=700
    #         )
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
            scaled_img.close()
            del scaled_img
            self.malloc_service.reduce_memory()
            return ret_image_path

    def move_to_storage(self, from_file, to_file):
        from cy_file_cryptor.context import create_encrypt
        count=10
        while count>0:
            if os.path.isfile(from_file):
                count=0
            else:
                time.sleep(1)
                count-=1
        with create_encrypt(to_file):
            with open(to_file, "wb") as fw:
                with open(from_file, "rb") as fr:
                    data_read = fr.read(1024)
                    while data_read:
                        fw.write(data_read)
                        del data_read
                        data_read = fr.read(1024)
                        self.malloc_service.reduce_memory()

        os.remove(from_file)

    def run_generate_image(self, file_type, file_process,server_file,size,cache_key,app_name,upload_id, is_in_thred):
        def running(abs_file_path,server_file,size,key):
            if file_type=="office":
                data = self.remote_caller_service.get_image_from_office(
                    url=f"{config.remote_office}",
                    local_file=abs_file_path,
                    remote_file=server_file,
                    memcache_server = config.cache_server
                )
                if data.get("error"):
                    print(json.dumps(data.get("error"),indent=4))
                    del data
                    self.malloc_service.reduce_memory()
                    return
                if data.get("image_file"):
                    office_image_file=data.get("image_file")
                    self.move_to_storage(
                        from_file=office_image_file,
                        to_file = f"{abs_file_path}.png"
                    )

                    ret = self.do_scale_size(file_path=f"{abs_file_path}.png", size=size)
                    self.memcache_services.set_str(key, ret)
                    return ret
            if file_type=="pdf":
                data = self.remote_caller_service.get_image_from_office(
                    url=f"{config.remote_pdf}",
                    local_file=abs_file_path,
                    remote_file=server_file,
                    memcache_server=config.cache_server
                )
                if data.get("image_file"):
                    office_image_file=data.get("image_file")
                    self.move_to_storage(
                        from_file=office_image_file,
                        to_file = f"{abs_file_path}.png"
                    )

                    ret = self.do_scale_size(file_path=f"{abs_file_path}.png", size=size)
                    self.memcache_services.set_str(key, ret)
                    return ret
            if file_type=="video":
                data = self.remote_caller_service.get_image_from_office(
                    url=f"{config.remote_video}",
                    local_file=abs_file_path,
                    remote_file=server_file,
                    memcache_server=config.cache_server
                )
                if data.get("image_file"):
                    video_image_file=data.get("image_file")
                    self.move_to_storage(
                        from_file=video_image_file,
                        to_file = f"{abs_file_path}.png"
                    )

                    ret = self.do_scale_size(file_path=f"{abs_file_path}.png", size=size)
                    self.memcache_services.set_str(key, ret)
                    return ret

        def running_if_fail_raise_message(abs_file_path,server_file,size,key):

            try:
                running(abs_file_path, server_file, size, key)
            except Exception as ex:
                upload = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.Id==upload_id
                )
                if not upload:
                    return
                self.msg.emit(
                    app_name=app_name,
                    data=upload,
                    message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE
                )
                print(traceback.format_exc())
        if is_in_thred:
            th=threading.Thread(target=running_if_fail_raise_message,args=(file_process,server_file,size,cache_key,))
            th.start()
        else:
            running_if_fail_raise_message(file_process,server_file,size,cache_key)


