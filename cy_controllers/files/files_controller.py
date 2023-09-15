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
from cy_xdoc.auths import Authenticate
import cy_kit
from cy_xdoc.services.files import FileServices
from cyx.common.file_storage import FileStorageService
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

import traceback
import humanize

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService,MongoDbFileStorage
)

__cache__ = dict()
__cache_thread__ = dict()

@controller.resource()
class FilesController:
    dependencies = [
        Depends(Authenticate)
    ]
    msg_service = cy_kit.singleton(RabitmqMsg)
    file_service: FileServices = cy_kit.singleton(FileServices)
    file_storage_service: MongoDbFileService = cy_kit.singleton(MongoDbFileService)
    msg_service: MessageService = cy_kit.singleton(MessageService)
    broker: Broker = cy_kit.singleton(Broker)
    temp_files = cy_kit.singleton(TempFiles)

    def __init__(self, request: Request):
        self.request = request

    async def get_upload_binary_async(self, FilePart: UploadFile):
        content_part = await FilePart.read(FilePart.size)
        FilePart.close()
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
        global __cache__
        key = f"{self.request.url.path}/{app_name}/{upload_id}"
        del __cache__[key]

    async def get_upload_register_async(self, app_name, upload_id):
        global __cache__
        key = f"{self.request.url.path}/{app_name}/{upload_id}"
        if __cache__.get(key) is None:
            upload_item = await self.file_service.get_upload_register_async(
                app_name=app_name,
                upload_id=upload_id
            )
            __cache__[key] = upload_item
            return upload_item
        else:
            return __cache__[key]

    async def push_file_to_temp_folder_async(self, app_name, content, upload_id, file_ext):
        def pushing_file():
            self.temp_files.push(
                app_name=app_name,
                content=content,
                upload_id=upload_id,
                file_ext=file_ext
            )

        pushing_file_th = threading.Thread(target=pushing_file)
        pushing_file_th.start()
        pushing_file_th.join()

    async def get_main_file_id_async(self, fs):
        return await fs.get_id_async()

    async def update_upload_status_async(self,
                                         app_name,
                                         upload_id,
                                         size_uploaded,
                                         num_of_chunks_complete,
                                         status,
                                         main_file_id):
        upload_register_doc = self.file_service.db_connect.db(app_name).doc(DocUploadRegister)

        def update_process():
            upload_register_doc.context.update(
                upload_register_doc.fields.Id == upload_id,
                upload_register_doc.fields.SizeUploaded << size_uploaded,
                upload_register_doc.fields.NumOfChunksCompleted << num_of_chunks_complete,
                upload_register_doc.fields.Status << status,
                upload_register_doc.fields.MainFileId << main_file_id,
                # upload_register_doc.fields.FileModuleController << file_controller

            )


        threading.Thread(target=update_process).start()
        data = await self.get_upload_register_async(
            app_name=app_name,
            upload_id=upload_id
        )
        data["SizeUploaded"] = size_uploaded
        data["NumOfChunksCompleted"] = num_of_chunks_complete
        data["status"] = status
        data["MainFileId"] = main_file_id

    async def push_file_async(self,app_name:str,upload_id:str, fs:MongoDbFileStorage, content_part, Index):
        # global __cache_thread__
        # thread_name = f"{app_name}/{upload_id}"
        # if __cache_thread__.get(thread_name) is None:
        #     __cache_thread__[thread_name] = threading.Thread()
        #     __cache_thread__[thread_name].start()

        def pushing_file():
            fs.push(content_part, Index)
        th = threading.Thread(target=pushing_file)
        th.start()
        th.join()



    async def update_search_engine_async(self, app_name, id, content, data_item, update_meta):
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
            print(f"raise msg {cyx.common.msg.MSG_FILE_UPLOAD}")
            try:
                self.broker.emit(
                    app_name=app_name,
                    message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                    data=data
                )
                print(f"raise msg {cyx.common.msg.MSG_FILE_UPLOAD} is ok")

                upload_register_doc.context.update(
                    upload_register_doc.fields.Id == upload_id,
                    upload_register_doc.fields.BrokerMsgUploadIsOk << True
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
        start_time = datetime.datetime.utcnow()
        s = datetime.datetime.utcnow()
        content_part = await self.get_upload_binary_async(FilePart)

        n = (datetime.datetime.utcnow() - s).total_seconds()
        print(FilePart.file.name)
        print(f"read file from request = {n}")
        upload_item = await self.get_upload_register_async(
            app_name=app_name,
            upload_id=UploadId
        )

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
        main_file_id = upload_item.MainFileId
        chunk_size_in_bytes = upload_item.ChunkSizeInBytes or 0
        server_file_name = upload_item.FullFileNameLower
        content_type, _ = mimetypes.guess_type(server_file_name)

        if num_of_chunks_complete == 0:
            s = datetime.datetime.utcnow()
            fs = await self.create_storage_file_async(
                app_name=app_name,
                rel_file_path=server_file_name,
                chunk_size=chunk_size_in_bytes,
                content_type=content_type,
                size=file_size
            )

            await self.push_file_async(
                app_name = app_name,
                upload_id= UploadId,
                fs = fs,
                content_part = content_part,
                Index =Index
            )

            upload_item.MainFileId = await self.get_main_file_id_async(fs)

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

            await self.push_file_async(
                app_name = app_name,
                upload_id=UploadId,
                fs = fs,
                content_part = content_part,
                Index =Index
            )
            if self.temp_files.is_use:
                s = datetime.datetime.utcnow()
                await self.temp_files.push_async(
                    app_name=app_name,
                    content=content_part,
                    upload_id=UploadId,
                    file_ext=upload_item[upload_register_doc.fields.FileExt]
                )
                n = (datetime.datetime.utcnow() - s).total_seconds()
                print(f"temp_files.push_async = {n}")
        if num_of_chunks_complete == nun_of_chunks - 1 and self.temp_files.is_use:
            upload_item["Status"] = 1
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

        n = (datetime.datetime.utcnow() - s).total_seconds()
        print(f"upload_register_doc.context.update_async = {n}")

        s = datetime.datetime.utcnow()
        ret_data = ret.to_pydantic()
        n = (datetime.datetime.utcnow() - s).total_seconds()
        print(f"data.to_pydantic()= {n}")
        total_time = (datetime.datetime.utcnow() - start_time).total_seconds()
        print(f"total_time= {total_time}")
        del FilePart

        if status == 1:
            self.delete_cache_upload_register(
                app_name=app_name,
                upload_id=UploadId
            )

        return ret_data
