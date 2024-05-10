import datetime
import gc

from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    UploadFile,
    Form, File
)

import bson
from cy_xdoc.auths import Authenticate
import cy_kit
from cy_xdoc.services.files import FileServices

from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
from cy_controllers.models.files_upload import (
    UploadChunkResult, ErrorResult, UploadFilesChunkInfoResult
)
import datetime
import mimetypes
import threading
from typing import Annotated
from fastapi.requests import Request
import traceback
import humanize
from cyx.common.msg import MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService, MongoDbFileStorage
)

from cyx.cache_service.memcache_service import MemcacheServices
from cy_controllers.common.base_controller import BaseController


async def get_main_file_id_async(fs):
    st = datetime.datetime.utcnow()
    ret = await fs.get_id_async()
    n = (datetime.datetime.utcnow() - st).total_seconds()
    print(f"get_main_file_id_async={n}")
    return ret


@controller.resource()
class FilesUploadController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        super().__init__(request)

    async def get_upload_binary_async(self, FilePart: UploadFile):
        content_part = await FilePart.read(FilePart.size)
        await FilePart.close()
        return content_part

    async def create_storage_file_async(self, app_name, rel_file_path, chunk_size, content_type, size):
        fs = await self.file_storage_service.create_async(
            app_name=app_name,
            rel_file_path=rel_file_path,
            chunk_size=chunk_size,
            content_type=content_type,
            size=size)
        return fs

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

    async def push_file_async(self, app_name: str, upload_id: str, fs: MongoDbFileStorage, content_part, Index):

        st = datetime.datetime.utcnow()

        def pushing_file():
            fs.push(content_part, Index)

        th = threading.Thread(target=pushing_file)
        th.start()
        th.join()
        n = (datetime.datetime.utcnow() - st).total_seconds()
        print(f"push_file_async={n}")

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
            print(e)

    async def post_msg_upload_file_async(self, app_name, data, upload_id):
        upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)

        def post_msg_upload():
            if data[upload_register_doc.fields.FileExt] is None:
                return
            try:
                local_share_id = self.local_api_service.generate_local_share_id(app_name=app_name, upload_id=data.id)
                data.local_share_id = local_share_id
                self.extract_content_service.save_search_engine(
                    data = data,
                    app_name = app_name
                )
                self.image_service.generate_image(
                    data=data,
                    app_name=app_name
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
        "/api/{app_name}/files/upload", summary="Upload file"
    )
    async def upload_async(self,
                           app_name: str,
                           UploadId: Annotated[str, Form()],
                           Index: Annotated[int, Form()],
                           FilePart: Annotated[UploadFile, File()]) -> UploadFilesChunkInfoResult:
        try:

            content_part = await self.get_upload_binary_async(FilePart)
            upload_item = self.file_service.get_upload_register_with_cache(
                app_name=app_name,
                upload_id=UploadId
            )
            # if upload_item.StorageType == "onedrive":
            #     from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
            #     try:
            #         res_upload = self.fucking_azure_onedrive_service.upload_content(
            #             session_url=upload_item.OnedriveSessionUrl,
            #             content=content_part,
            #             chunk_size=upload_item.ChunkSizeInBytes,
            #             file_size=upload_item.SizeInBytes,
            #             chunk_index=Index
            #         )
            #         print(res_upload)
            #     except FuckingWhoreMSApiCallException as e:
            #         ret_error = UploadFilesChunkInfoResult()
            #         ret_error.Error = ErrorResult(
            #             Code=e.code,
            #             Message=e.message,
            #             Fields=["Error from microsoft onedrive"]
            #         )
            #         return ret_error

            if upload_item is None:
                del FilePart
                del content_part
                return cy_docs.DocumentObject(
                    Error=dict(
                        Message="Upload was not found or has been remove",
                        Code="ItemWasNotFound"

                    )
                ).to_pydantic()
            upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)
            file_size = upload_item.SizeInBytes
            # path_to_broker_share = os.path.join(path_to_broker_share,f"{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}")
            size_uploaded = upload_item.SizeUploaded or 0
            num_of_chunks_complete = upload_item.NumOfChunksCompleted or 0
            nun_of_chunks = upload_item.NumOfChunks or 0
            # main_file_id = upload_item.MainFileId
            chunk_size_in_bytes = upload_item.ChunkSizeInBytes or 0
            server_file_name = upload_item.FullFileNameLower
            content_type, _ = mimetypes.guess_type(server_file_name)

            if num_of_chunks_complete == 0:
                fs = await self.create_storage_file_async(
                    app_name=app_name,
                    rel_file_path=server_file_name,
                    chunk_size=chunk_size_in_bytes,
                    content_type=content_type,
                    size=file_size
                )

                await self.push_file_async(
                    app_name=app_name,
                    upload_id=UploadId,
                    fs=fs,
                    content_part=content_part,
                    Index=Index
                )

                upload_item.MainFileId = await get_main_file_id_async(fs)

                main_file_id = upload_item.MainFileId
                if not upload_item.MainFileId.startswith("local://"):
                    await self.push_file_to_temp_folder_async(
                        app_name=app_name,
                        content=content_part,
                        upload_id=UploadId,
                        file_ext=upload_item[upload_register_doc.fields.FileExt]
                    )
            else:
                fs = await self.file_storage_service.get_file_by_name_async(
                    app_name=app_name,
                    rel_file_path=server_file_name
                )
                if not upload_item.MainFileId.startswith("local://"):
                    await self.push_file_async(
                        app_name=app_name,
                        upload_id=UploadId,
                        fs=fs,
                        content_part=content_part,
                        Index=Index
                    )
                    await self.push_temp_file_async(
                        app_name=app_name,
                        content=content_part,
                        upload_id=UploadId,
                        file_ext=upload_item[upload_register_doc.fields.FileExt]
                    )
                await self.push_file_async(
                    app_name=app_name,
                    upload_id=UploadId,
                    fs=fs,
                    content_part=content_part,
                    Index=Index
                )
            if num_of_chunks_complete == nun_of_chunks - 1 and self.temp_files.is_use:
                upload_item["Status"] = 1
                if upload_item.get("SkipActions") is None or (isinstance(upload_item.get("SkipActions"), dict) and (
                        upload_item["SkipActions"].get(MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE, False) == False and
                        upload_item["SkipActions"].get("All", False) == False
                )):
                    await self.update_search_engine_async(
                        app_name=app_name,
                        id=UploadId,
                        content="",
                        data_item=upload_item,
                        update_meta=False
                    )
                if upload_item.get("SkipActions") is None or (isinstance(upload_item.get("SkipActions"), dict) and (
                        upload_item["SkipActions"].get("All", False) == False
                )):

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


            status = 0
            if num_of_chunks_complete == nun_of_chunks:
                status = 1

            await self.update_upload_status_async(
                app_name=app_name,
                upload_id=UploadId,
                size_uploaded=size_uploaded,
                num_of_chunks_complete=num_of_chunks_complete,
                status=status,
                main_file_id=fs.get_id()
            )
            upload_item.SizeUploaded = size_uploaded
            upload_item.NumOfChunksCompleted = num_of_chunks_complete
            upload_item.Status = status
            upload_item.MainFileId = fs.get_id()
            self.file_service.set_upload_register_to_cache(
                app_name=app_name,
                upload_id=UploadId,
                data=upload_item
            )

            ret_data = ret.to_pydantic()

            if status == 1:
                map = {
                    "onedrive": "Azure",
                    "google-drive": "Google",
                    "s3":"AWS"
                }
                if map.get(upload_item.StorageType):



                    self.cloud_service_utils.do_sync_data(
                        app_name=app_name,
                        cloud_name=map.get(upload_item.StorageType),
                        upload_item= upload_item

                    )

                self.delete_cache_upload_register(
                    app_name=app_name,
                    upload_id=UploadId
                )


            return ret_data

        except Exception as ex:
            # self.logger_service.error(ex, more_info=dict(
            #     app_name=app_name,
            #     UploadId=UploadId,
            #     Index=Index
            # ))
            import traceback
            ret = UploadFilesChunkInfoResult()
            ret.Error = ErrorResult()
            ret.Error.Code = "System"
            ret.Error.Message =repr(ex)
            return ret

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

