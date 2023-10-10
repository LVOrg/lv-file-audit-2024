import datetime
import gc
import typing
import uuid

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
    Form, File,Body
)
from cy_xdoc.auths import Authenticate
import cy_xdoc.models.files
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

router = APIRouter()
controller = Controller(router)
import threading
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService,MongoDbFileStorage
)

from cyx.cache_service.memcache_service import MemcacheServices
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import (
    FileUploadRegisterInfo,DataMoveTanent,DataMoveTanentParam
)
import cy_web
@controller.resource()
class FilesController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.router.post("/api/{app_name}/files/mark_delete")
    async def mark_delete(self,app_name: str, UploadId:typing.Optional[str]=Body(...), IsDelete: typing.Optional[bool]=Body(...)):
        """
        Danh dau xoa
        :param app_name:
        :param UploadId:
        :param IsDelete: True if mark deleted False if not
        :param token:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        # file_services: cy_xdoc.services.files.FileServices = cy_kit.singleton(cy_xdoc.services.files.FileServices)
        # search_services: cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(
        #     cy_xdoc.services.search_engine.SearchEngine)
        doc_context =  self.file_service.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        delete_item = doc_context.context @ UploadId
        if delete_item is None:
            return {}
        # gfs = db_context.get_grid_fs()
        # main_file_id = delete_item.get(Files.MainFileId.__name__)

        ret = doc_context.context.update(
            doc_context.fields.id == UploadId,
            doc_context.fields.MarkDelete << IsDelete
        )
        self.search_engine.mark_delete(app_name=app_name, id=UploadId, mark_delete_value=IsDelete)

        # search_engine.get_client().delete(index=fasty.configuration.search_engine.index, id=es_id)
        return dict()


    @controller.router.post("/api/{app_name}/files")
    async def get_list(
            self,
            app_name: str,
            PageSize: int = Body(...),
            PageIndex: int = Body(...),
            FieldSearch: typing.Optional[str] = Body(default=None),
            ValueSearch: typing.Optional[str] = Body(default=None)):
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)

        items =self.file_service.get_list(
            app_name=app_name,
            root_url=cy_web.get_host_url(),
            page_size=PageSize,
            page_index=PageIndex,
            field_search=FieldSearch,
            value_search=ValueSearch

        )
        return [x.to_pydantic() for x in items]



    @controller.router.post("/api/admin/files/move_tenant")
    def move_tenant(self,data:typing.Optional[DataMoveTanentParam] = Body(...)):
        Data=data.Data
        if not self.app_service.get_item(
                app_name='admin',
                app_get=Data.FromAppName
        ):
            return dict(
                error=dict(
                    message=f"{Data.FromAppName} was not found"
                )
            )
        if not self.app_service.get_item(
                app_name='admin',
                app_get=Data.ToAppName
        ):
            return dict(
                error=dict(
                    message=f"{Data.ToAppName} was not found"
                )
            )
        if Data.FromAppName == Data.ToAppName:
            return dict(
                error=dict(
                    message=f"Can not move from '{Data.FromAppName}' to '{Data.ToAppName}'"
                )
            )
        from cy_xdoc.services.files import FileServices
        from cyx.common.file_storage_mongodb import MongoDbFileStorage
        from cyx.common.brokers import Broker
        from cyx.common.temp_file import TempFiles
        # file_service: FileServices = cy_kit.singleton(FileServices)
        # file_storage_service: MongoDbFileStorage = cy_kit.singleton(MongoDbFileStorage)

        # broker: Broker = cy_kit.singleton(Broker)
        obsever_id = str(uuid.uuid4())
        self.msg_service.emit(
            app_name="admin",
            message_type=cyx.common.msg.MSG_FILE_MOVE_TENANT,
            data=dict(
                from_app=Data.FromAppName,
                to_app=Data.ToAppName,
                ids=Data.UploadIds,
                obsever_id=obsever_id
            )
        )
        return obsever_id