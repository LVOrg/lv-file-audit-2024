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
from gradio_client import Client
__version__ = "0.5"


from cyx.common.rabitmq_message import RabitmqMsg


class ThumbService:
    def __init__(
            self,
            memcache_services=cy_kit.singleton(MemcacheServices),
            mongodb_service=cy_kit.singleton(MongodbService),
            msg=cy_kit.singleton(RabitmqMsg)
    ):
        self.memcache_services: MemcacheServices = memcache_services
        self.cache_group = f"/{__version__}/{config.file_storage_path}/{__file__}/{type(self).__name__}/thumb"
        self.mongodb_service = mongodb_service
        self.msg = msg

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

    def get_thumb_path_from_image(self, in_path, size, main_file_path):
        process_services_host = config.process_services_host or "http://localhost"
        try:
            txt_json = json.dumps(dict(
                in_path=in_path,
                size=size,
                main_file_path=main_file_path,
                mem_cache_server = config.cache_server
            ))
            client = Client(f"{process_services_host}:1114/")
            _, result = client.predict(
                txt_json,
                False,
                api_name="/predict"
            )
        except Exception as ex:
            print(ex)
        print(in_path,size,main_file_path)
        ret = os.path.join(pathlib.Path(in_path).parent.__str__(),f"{size}.webp")
        if os.path.isfile(ret):
            return ret


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
