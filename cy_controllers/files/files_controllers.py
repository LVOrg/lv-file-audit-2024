import datetime
import gc
import typing
import uuid

import pydantic
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
from fastapi import responses
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
from cy_controllers.models import (
    files as controller_model_files
)
from cyx.cache_service.memcache_service import MemcacheServices
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import (
    FileUploadRegisterInfo,
    DataMoveTanent,
    DataMoveTanentParam,
    FileContentSaveData,
    FileContentSaveResult,
    CloneFileResult,
    FileContentSaveArgs,
    ErrorInfo,
    AddPrivilegesResult,
    PrivilegesType
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
        try:
            items =self.file_service.get_list(
                app_name=app_name,
                root_url=cy_web.get_host_url(),
                page_size=PageSize,
                page_index=PageIndex,
                field_search=FieldSearch,
                value_search=ValueSearch

            )
            return [x.to_pydantic() for x in items]
        except Exception as e:
            self.logger_service.error(e)
            return []



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

    @controller.router.post("/api/{app_name}/files/clone")
    def clone_to_new(self,
                     app_name: str,
                     UploadId: typing.Annotated[str,Body(embed=True)]) -> CloneFileResult:



        item = self.file_service.do_copy(app_name=app_name, upload_id=UploadId)

        if item is None:
            return CloneFileResult(
                Error=pydantic.BaseModel(
                    Code="fileNotFound",
                    Message="File not found"

                )
            )
        else:

            return CloneFileResult(
                Info=item.to_json_convertable()
            )

    @controller.router.post("/api/{app_name}/files/delete")
    def files_delete(self,app_name: str, UploadId: typing.Annotated[str,Body(embed=True)])->controller_model_files.DeleteFileResult:
        ret = controller_model_files.DeleteFileResult()
        try:
            self.file_service.remove_upload(app_name=app_name, upload_id=UploadId)
            ret.AffectedCount =1
            return ret
        except FuckingWhoreMSApiCallException  as e:
            ret.Error = controller_model_files.ErrorInfo()
            ret.Error.Code = e.code,
            ret.Error.Message = e.message
            return ret
        except Exception as e:
            self.logger_service.error(e)
            return responses.JSONResponse(
                content= dict(
                    Code="system",
                    Message=str(e)

                ),
                status_code=500
            )




    @controller.router.post("/api/{app_name}/content/save")
    def file_content_save(
            self,
            app_name: str,
            args: FileContentSaveArgs):
        """
        Insert or update more data to UploadRegister<br/>
        Chèn hoặc cập nhật thêm dữ liệu vào UploadRegister
        :param app_name:
        :param doc_id:
        :param data:
        :param token:
        :return:
        """
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        data = args.data
        if not data.DocId or data.DocId == "":
            data.DocId = str(uuid.uuid4())

        data_item =self.file_service.get_upload_register(
            app_name=app_name,
            upload_id=data.DocId,

        )
        if data_item and data.Privileges:
            json_privilege = {}
            for x in data.Privileges or []:
                if json_privilege.get(x.Type.lower()):
                    json_privilege[x.Type.lower()] += x.Values.split(',')
                else:
                    json_privilege[x.Type.lower()] = x.Values.split(',')
            data_item["Privileges"] = json_privilege
        else:
            _source = self.search_engine.get_doc(
                app_name=app_name,
                id=data.DocId
            )
            _source_data_item = None
            if _source:
                _source_data_item = _source.source.data_item
            fx = DocUploadRegister()

            json_privilege = {}
            for x in data.Privileges or []:
                if json_privilege.get(x.Type.lower()):
                    json_privilege[x.Type.lower()] += x.Values.split(',')
                else:
                    json_privilege[x.Type.lower()] = x.Values.split(',')

            data_item = _source_data_item or {
                "FileName": "Unknown",
                "Status": 1,
                "MarkDelete": False,
                "RegisterOn": datetime.datetime.utcnow(),
                "_id": data.DocId,
                "SizeInBytes": 0,
                "Privileges": json_privilege
            }
            if data.Privileges is not None:
                data_item["Privileges"] = json_privilege

        self.search_engine.update_content(
            app_name=app_name,
            content=data.Content,
            data_item=data_item,
            meta_info=data.MetaData,
            id=data.DocId,
            replace_content=True
        )
        data_item["Id"] = data.DocId
        import cy_docs
        return data_item.to_json_convertable() if isinstance(data_item, cy_docs.DocumentObject) else data_item

    @controller.router.post("/api/{app_name}/files/content-re-process")
    def file_content_re_process(
            self,
            app_name: str,
            UploadIds: typing.List[str]= Body(embed=True)):
        # from cy_xdoc.controllers.apps import check_app
        # check_app(app_name)
        ret = []
        for UploadId in UploadIds:
            upload_item = self.file_service.get_upload_register(app_name, upload_id=UploadId)
            if upload_item:
                try:
                    self.msg_service.emit(
                        app_name=app_name,
                        message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                        data=upload_item
                    )
                    ret += [{
                        "UploadId": UploadId,
                        "Message": "Is in processing"
                    }]
                    self.logger_service.info(f"rais msg {cyx.common.msg.MSG_FILE_UPLOAD}")
                except Exception as e:
                    ret += [{
                        "UploadId": UploadId,
                        "Message": "Error broker"
                    }]

            else:
                ret += [{
                    "UploadId": UploadId,
                    "Message": "Content was not found"
                }]

        return ret

    @controller.router.post("/api/{app_name}/files/info")
    def get_info(self, app_name: str, UploadId:str=Body(embed=True)) -> controller_model_files.UploadInfoResult:
        """
        APi này lay chi tiet thong tin cua Upload
        :param app_name:
        :return:
        """

        doc_context = self.file_service.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        upload_info = doc_context.context @ UploadId
        if upload_info is None:
            return None
        upload_info.UploadId = upload_info._id
        upload_info.HasOCR = upload_info.OCRFileId is not None
        upload_info.RelUrl = f"api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.FullUrl = f"{cy_web.get_host_url()}/api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
        upload_info.HasThumb = upload_info.ThumbFileId is not None
        available_thumbs = upload_info.AvailableThumbs or []
        upload_info.AvailableThumbs = []
        for x in available_thumbs:
            upload_info.AvailableThumbs += [f"api/{app_name}/{x}"]
        if upload_info.HasThumb:
            """
            http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
            """
            upload_info.RelUrlThumb = f"api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
            upload_info.UrlThumb = f"{cy_web.get_host_url()}/api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
        if upload_info.HasOCR:
            """
            http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
            """
            upload_info.RelUrlOCR = f"api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
            upload_info.UrlOCR = f"{cy_web.get_host_url()}/api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
        if upload_info.VideoResolutionWidth:
            upload_info.VideoInfo = cy_docs.DocumentObject()
            upload_info.VideoInfo.Width = upload_info.VideoResolutionWidth
            upload_info.VideoInfo.Height = upload_info.VideoResolutionHeight
            upload_info.VideoInfo.Duration = upload_info.VideoDuration
        if upload_info.ClientPrivileges and not isinstance(upload_info.ClientPrivileges, list):
            upload_info.ClientPrivileges = [upload_info.ClientPrivileges]
        if upload_info.ClientPrivileges is None:
            upload_info.ClientPrivileges = []
        if upload_info[doc_context.fields.RemoteUrl]:
            upload_info[cy_docs.fields.FullUrl] = upload_info[doc_context.fields.RemoteUrl]
        return upload_info.to_pydantic()


