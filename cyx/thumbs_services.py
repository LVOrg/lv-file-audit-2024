import json
import mimetypes
import os.path
import pathlib
import threading
import time
import traceback
import typing
from datetime import datetime

import bson.objectid
import cy_file_cryptor.context
import cy_kit
import cyx.common.msg
from cyx.cache_service.memcache_service import MemcacheServices

from cyx.common.mongo_db_services import MongodbService
from cyx.common import config
from cyx.remote_caller import RemoteCallerService
__version__ = "0.5"
from functools import cache
import hashlib
import webp
from PIL import Image, UnidentifiedImageError
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
from cyx.malloc_services import MallocService
import requests
from cyx.file_utils_services import FileUtilService
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
class ThumbService:
    memcache_services = cy_kit.singleton(MemcacheServices)
    mongodb_service = cy_kit.singleton(MongodbService)
    msg = cy_kit.singleton(RabitmqMsg)
    local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService)
    remote_caller_service: RemoteCallerService = cy_kit.singleton(RemoteCallerService)
    malloc_service = cy_kit.singleton(MallocService)
    cache_group = f"/v03/{config.file_storage_path}/ThumbService/thumb"
    file_util_service = cy_kit.singleton(FileUtilService)
    logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)
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

    async def get_async(self, app_name: str, directory: str, size: int)->typing.Union[str,bson.ObjectId]|None:
        key = self.get_cache_key(app_name=app_name,directory=directory,size=size)
        ret= self.memcache_services.get_str(key)
        if ret and os.path.isfile(ret) and os.stat(ret).st_size>0:
            return ret


        upload_id = directory.split('/')[0]
        original_file_path = await self.file_util_service.get_physical_path_async(app_name,upload_id)
        if original_file_path is None:
            return None
        original_dir = pathlib.Path(original_file_path).parent.__str__()
        thumb_file_path = os.path.join(original_dir,f"{size}.webp")
        if os.path.isfile(thumb_file_path) and os.stat(thumb_file_path).st_size>0:
            self.memcache_services.set_str(key,thumb_file_path)
            return thumb_file_path

        upload_item = self.file_util_service.get_upload(
            app_name = app_name,
            upload_id = upload_id
        )

        if upload_item is None:
            return None
        thumb_id = upload_item.get(Repository.files.fields.ThumbFileId.__name__)
        if isinstance(thumb_id, bson.ObjectId):
            return thumb_id
        if bson.ObjectId.is_valid(thumb_id):
            return bson.ObjectId(thumb_id) if isinstance(thumb_id,str) else thumb_id


        real_file_path = await self.file_util_service.get_physical_path_async(
            app_name=app_name,
            upload_id=upload_id
        )
        if real_file_path is None:
            return None
        if check_ext_file:=upload_item.get(Repository.files.fields.FileExt.__name__):
            mime_type, _ = mimetypes.guess_type(f'test.{check_ext_file}')
        else:
            mime_type, _ = mimetypes.guess_type(real_file_path)


        if mime_type.startswith("image/"):
            download_file_path, _, _, _, _ = self.local_api_service.get_download_path(
                upload_item=upload_item,
                app_name=app_name
            )
            upload_file_path = self.local_api_service.get_upload_path(
                upload_item=upload_item,
                app_name=app_name,
                file_name=f"{size}.webp"
            )
            self.remote_caller_service.get_thumb(
                url_of_thumb_service = config.remote_thumb,
                url_of_image = download_file_path,
                url_upload_file = upload_file_path,
                size = size
            )

            return real_file_path

        main_field_id = upload_item.get(Repository.files.fields.MainFileId.__name__)
        if (bson.objectid.ObjectId.is_valid(main_field_id)):
            """
            Recalculate file storage and location if upload's file is still in mongoDb
            """
            file_ext="unknown"
            if upload_item.get(Repository.files.fields.FileExt.__name__):
                file_ext = upload_item.get(Repository.files.fields.FileExt.__name__).lower()[0:3]
            register_on = datetime.fromisoformat(upload_item.get(Repository.files.fields.RegisterOn.__name__))
            rel_path =  f'{app_name}/{register_on.strftime("%Y/%m/%d")}/{file_ext}/{upload_id}/{upload_item[Repository.files.fields.FileName].lower()}'
            folder_path = os.path.join(config.file_storage_path, app_name,
                                       register_on.strftime("%Y/%m/%d").replace('/', os.sep),file_ext, upload_id)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, upload_item.get(Repository.files.fields.FileName.__name__).lower())

            server_file = config.private_web_api +f"/api/{app_name}/file/{upload_item.get('_id')}/{upload_item[Repository.files.fields.FileName].lower()}"
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

        if not upload_item.get(Repository.files.fields.FileExt.__name__):
            return None
        server_file, rel_file_path, download_file_path, token, local_share_id = self.local_api_service.get_download_path(
            upload_item=upload_item,
            app_name=app_name
        )


        file_path_image = f'{rel_file_path}.png'
        if os.path.isfile(file_path_image) and os.stat(file_path_image).st_size>0:
            download_file_path, _, _, _, _ = self.local_api_service.get_download_path(
                upload_item=upload_item,
                app_name=app_name,
                to_file_ext="png"
            )
            upload_file_path = self.local_api_service.get_upload_path(
                upload_item=upload_item,
                app_name=app_name,
                file_name=f"{size}.webp"
            )
            self.remote_caller_service.get_thumb(
                url_of_thumb_service=config.remote_thumb,
                url_of_image=download_file_path,
                url_upload_file=upload_file_path,
                size = size
            )

            return file_path_image


        file_ext = upload_item.get(Repository.files.fields.FileExt.__name__)
        file_type = self.get_thumb_type(file_ext)



        folder_dir = pathlib.Path(real_file_path).parent.__str__()
        thumb_file = os.path.join(folder_dir,f"{size}.webp")

        if os.path.isfile(thumb_file) and os.stat(thumb_file).st_size>0:
            self.memcache_services.set_str(key,thumb_file)
            return thumb_file
        image_file = real_file_path
        if file_type !="image":
            image_file=f"{real_file_path}.png"
        if os.path.isfile(image_file) and os.stat(image_file).st_size>0:
            url_of_image = server_file.split('?')[0]+".png"+"?"+server_file.split("?")[1]
            url_upload_file = self.local_api_service.get_upload_path(
                upload_item=upload_item,
                app_name=app_name,
                file_name=f"{size}.webp"
            )
            self.remote_caller_service.get_thumb(
                url_of_thumb_service= config.remote_thumb,
                url_of_image = url_of_image,
                url_upload_file = url_upload_file,
                size=size

            )
            return image_file

        else:
            self.run_generate_image(file_type=file_type,
                                    file_process=real_file_path,
                                    is_in_thred=True,
                                    app_name=app_name,
                                    upload_id=upload_id,
                                    size=size,
                                    cache_key=key,
                                    server_file=server_file,
                                    )

        return None




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
        def running():
            upload_item = self.file_util_service.get_upload(
                app_name = app_name,
                upload_id = upload_id
            )
            real_file_path = self.file_util_service.get_physical_path(app_name=app_name,
                                                                                  upload_id=upload_item.get("_id"))
            file_name = pathlib.Path(real_file_path).name
            upload_url = self.local_api_service.get_upload_path(
                upload_item=upload_item,
                app_name=app_name,
                file_name=f'{file_name}',
                file_ext="png"

            )
            download_url, _, _, _, _ = self.local_api_service.get_download_path(
                upload_item=upload_item,
                app_name=app_name
            )


            if file_type=="office":

                self.remote_caller_service.get_image_from_office(
                    url_of_office_to_image_service=f"{config.remote_office}",
                    url_upload_file=upload_url,
                    url_of_content=download_url
                )

            elif file_type=="pdf":
                self.remote_caller_service.get_image_from_pdf(
                    download_url=download_url,
                    upload_url=upload_url
                )
            elif file_type=="video":
                self.remote_caller_service.get_image_from_video(
                    download_url=download_url,
                    upload_url=upload_url
                )
        def run_with_exception():
            try:
                running()
            except:
                self.logs_to_mongo_db_service.log(
                    error_content=traceback.format_exc(),
                    url=f'{type(self).__module__}/{type(self).__name__}/run_generate_image'
                )
        threading.Thread(target=run_with_exception).start()



