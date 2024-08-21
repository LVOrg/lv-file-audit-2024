
import typing
from cyx.repository import Repository
fx = Repository.files.fields.Status
from cyx.common import config
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    Form, File
)


from cyx.repository import Repository
from cy_xdoc.auths import Authenticate
from cyx.db_models.files import DocUploadRegister
from cy_controllers.models.files_upload import (
    ErrorResult, UploadFilesChunkInfoResult
)
import datetime
import mimetypes

from typing import Annotated
from fastapi.requests import Request
import traceback
import humanize
from cyx.common.msg import MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs



from cy_controllers.common.base_controller import BaseController

async def get_main_file_id_async(fs):
    st = datetime.datetime.utcnow()
    ret = await fs.get_id_async()
    n = (datetime.datetime.utcnow() - st).total_seconds()
    print(f"get_main_file_id_async={n}")
    return ret
import cy_file_cryptor.context
version2 = config.generation if hasattr(config,"generation") else None

@controller.resource()
class FilesUploadController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        super().__init__(request)
        self.cache_type = f"{DocUploadRegister.__module__}.{DocUploadRegister.__name__}"

    async def get_upload_binary_async(self, FilePart: UploadFile):
        content_part = await FilePart.read(FilePart.size)
        await FilePart.close()
        return content_part

    # async def create_storage_file_async(self, app_name, rel_file_path, chunk_size, content_type, size):
    #     fs = await self.file_storage_service.create_async(
    #         app_name=app_name,
    #         rel_file_path=rel_file_path,
    #         chunk_size=chunk_size,
    #         content_type=content_type,
    #         size=size)
    #     return fs

    def delete_cache_upload_register(self, app_name, upload_id):
        # global __cache__
        # key = f"{self.request.url.path}/{app_name}/{upload_id}"
        # del __cache__[key]
        pass

    async def get_upload_register_async(self, app_name, upload_id) -> cy_docs.DocumentObject:
        """
        This function use memcache
        :param app_name:
        :param upload_id:
        :return:
        """

        return self.file_service.get_upload_register(
            app_name=app_name,
            upload_id=upload_id
        )

    async def push_file_to_temp_folder_async(self, app_name, content, upload_id, file_ext):
        st = datetime.datetime.utcnow()

        def pushing_file():
            self.temp_files.push(
                app_name=app_name,
                content=content,
                upload_id=upload_id,
                file_ext=file_ext,
                sync_file_if_not_exit=False
            )

        pushing_file_th = threading.Thread(target=pushing_file)
        pushing_file_th.start()
        pushing_file_th.join()
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"push_file_to_temp_folder_async={n}")

    async def update_upload_status_async(self,
                                         app_name,
                                         upload_id,
                                         size_uploaded,
                                         num_of_chunks_complete,
                                         status,
                                         main_file_id):
        st = datetime.datetime.utcnow()
        upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"self.file_service.db_connect.db(app_name).doc(DocUploadRegister)={n}")
        import bson

        def update_process():
            upload_register_doc.context.update(
                upload_register_doc.fields.Id == upload_id,
                upload_register_doc.fields.SizeUploaded << size_uploaded,
                upload_register_doc.fields.NumOfChunksCompleted << num_of_chunks_complete,
                upload_register_doc.fields.Status << status,
                upload_register_doc.fields.MainFileId << main_file_id,
                upload_register_doc.fields.StoragePath << main_file_id
                # upload_register_doc.fields.FileModuleController << file_controller

            )

        st = datetime.datetime.utcnow()
        threading.Thread(target=update_process).start()
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"threading.Thread(target=update_process).start()={n}")
        st = datetime.datetime.utcnow()
        data = await self.get_upload_register_async(
            app_name=app_name,
            upload_id=upload_id
        )
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"await self.get_upload_register_async={n}")
        if not isinstance(data,dict):
            data = data.to_json_convertable()
        data["SizeUploaded"] = size_uploaded
        data["NumOfChunksCompleted"] = num_of_chunks_complete
        data["Status"] = status
        data["MainFileId"] = main_file_id

        data_from_cache = self.file_service.get_upload_register_with_cache(app_name=app_name, upload_id=upload_id)
        data_from_cache.SizeUploaded = size_uploaded
        data_from_cache.NumOfChunksCompleted = status
        data_from_cache.Status = num_of_chunks_complete
        data_from_cache.MainFileId = main_file_id
        data_from_cache.StoragePath = main_file_id



    async def update_search_engine_async(self, app_name, id, content, data_item, update_meta):
        """
        run in thread
        :param app_name:
        :param id:
        :param content:
        :param data_item:
        :param update_meta:
        :return:
        """
        try:
            def update_search_engine_content():
                if isinstance(config.elastic_search, bool):
                    return

                self.file_service.search_engine.update_content(
                    app_name=app_name,
                    id=id,
                    content=content,
                    data_item=data_item,
                    update_meta=update_meta

                )

            threading.Thread(target=update_search_engine_content, args=()).start()
        except Exception as e:
            raise e


    async def post_msg_upload_file_async(self, app_name: str, data:typing.Dict[typing.AnyStr,typing.Any], upload_id: str):
        upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)

        def post_msg_upload():
            if data.get(upload_register_doc.fields.FileExt.__name__) is None:
                return
            try:
                local_share_id = self.local_api_service.generate_local_share_id(app_name=app_name, upload_id=data.get("_id"))
                data[Repository.files.fields.local_share_id.__name__] = local_share_id
                self.extract_content_service.save_search_engine(
                    data = data,
                    app_name = app_name
                )





            except Exception as e:
                traceback_string = traceback.format_exc()
                upload_register_doc.context.update(
                    upload_register_doc.fields.Id == upload_id,
                    upload_register_doc.fields.BrokerErrorLog << traceback_string
                )
                print(traceback_string)
                print(e)

        threading.Thread(target=post_msg_upload, args=()).start()

    @controller.route.post(
        "/api/{app_name}/files/upload" if not version2 else "/api/{app_name}/files/upload_old", summary="Upload file",
        tags=["FILES"]
    )
    async def upload_async(self,
                           app_name: str,
                           UploadId: Annotated[str, Form()],
                           Index: Annotated[int, Form()],
                           FilePart: Annotated[UploadFile, File()]) :
        # try:

        content_part = await self.get_upload_binary_async(FilePart)
        upload_item = self.file_util_service.get_upload(
            app_name=app_name,
            upload_id=UploadId
        )


        if upload_item is None:
            del FilePart
            del content_part
            ret = UploadFilesChunkInfoResult()
            ret.Error =ErrorResult()
            ret.Error.Code="ItemWasNotFound"
            ret.Error.Message="Upload was not found or has been remove"
            return ret
        # upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)
        file_size = upload_item[Repository.files.fields.SizeInBytes.__name__]
        size_uploaded = upload_item[Repository.files.fields.SizeUploaded.__name__] or 0
        num_of_chunks_complete = upload_item[Repository.files.fields.NumOfChunksCompleted.__name__] or 0
        nun_of_chunks = upload_item[Repository.files.fields.NumOfChunks.__name__] or 0
        # chunk_size_in_bytes = upload_item[Repository.files.fields.ChunkSizeInBytes.__name__] or 0
        server_file_name = upload_item[Repository.files.fields.FullFileNameLower.__name__]
        content_type, _ = mimetypes.guess_type(server_file_name)
        if not upload_item.get("real_file_location"):
            file_path = await self.file_util_service.get_physical_path_async(
                app_name=app_name,
                upload_id=UploadId
            )
        else:
            file_path = upload_item.get("real_file_location")


        await self.file_util_service.save_file_single_thread_async(
            app_name=app_name,
            upload_id=UploadId,
            file_path =file_path,
            chunk_index=Index,
            content_part = content_part
        )
        """
        Save content is OK. Cache and infor of upload file in db has been changed
        """
        upload_item = self.file_util_service.get_upload(
            app_name=app_name,
            upload_id=UploadId
        )
        """
        Fetch again for new value ffrom cache
        """

        skip_action: typing.Dict[str,typing.Any]|None = upload_item.get(Repository.files.fields.SkipActions.__name__)
        if num_of_chunks_complete == nun_of_chunks - 1 and self.temp_files.is_use:


            if skip_action is None or (isinstance(skip_action, dict) and (
                    skip_action.get(MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE, False) == False and
                    skip_action.get("All", False) == False
            )):
                await self.update_search_engine_async(
                    app_name=app_name,
                    id=UploadId,
                    content="",
                    data_item=upload_item,
                    update_meta=False
                )
                await self.post_msg_upload_file_async(
                    app_name=app_name,
                    upload_id=UploadId,
                    data=upload_item
                )


        size_uploaded += len(content_part)
        ret = cy_docs.DocumentObject()
        ret.Data = cy_docs.DocumentObject()
        ret.Data.Percent = round((size_uploaded * 100) / file_size, 2)
        ret.Data.SizeUploadedInHumanReadable = humanize.filesize.naturalsize(size_uploaded)
        num_of_chunks_complete += 1
        ret.Data.NumOfChunksCompleted = num_of_chunks_complete
        ret.Data.SizeInHumanReadable = humanize.filesize.naturalsize(file_size)
        ret_data = ret.to_pydantic()
        media_status:int = upload_item[Repository.files.fields.Status.__name__]
        if media_status == 1:
            map = {
                "onedrive": "Azure",
                "google-drive": "Google",
                "s3":"AWS"
            }
            storage_type:str = upload_item[Repository.files.fields.StorageType.__name__]
            if map.get(storage_type):
                self.cloud_service_utils.do_sync_data(
                    app_name=app_name,
                    cloud_name=map.get(storage_type),
                    upload_item= upload_item
                )




        return ret_data

        # except Exception as ex:
        #     # self.logger_service.error(ex, more_info=dict(
        #     #     app_name=app_name,
        #     #     UploadId=UploadId,
        #     #     Index=Index
        #     # ))
        #     import traceback
        #     ret = UploadFilesChunkInfoResult()
        #     ret.Error = ErrorResult()
        #     ret.Error.Code = "System"
        #     ret.Error.Message =repr(ex)
        #     return ret
        # finally:
        #     del content_part
        #     self.malloc_service.reduce_memory()

    async def push_temp_file_async(self, app_name, content, upload_id, file_ext):
        st = datetime.datetime.utcnow()
        if self.temp_files.is_use:
            await self.temp_files.push_async(
                app_name=app_name,
                content=content,
                upload_id=upload_id,
                file_ext=file_ext
            )
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"push_temp_file_async={n}")

