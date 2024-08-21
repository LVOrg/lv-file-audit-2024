import datetime
import gc
import os
import pathlib
import typing
import uuid

import pydantic
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Body
)
from cy_xdoc.auths import Authenticate
import cyx.db_models.files

from cyx.common.msg import MessageService
from cyx.db_models.files import DocUploadRegister
import datetime
from cyx.repository import Repository

router = APIRouter()
controller = Controller(router)
import cyx.common.msg
from cy_controllers.models import (
    files as controller_model_files
)
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import (
    DataMoveTanentParam,
    CloneFileResult,
    FileContentSaveArgs,
    ErrorInfo,
    AddPrivilegesResult,
    PrivilegesType,
    CheckoutResource
)

import cy_web


@controller.resource()
class FilesController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/{app_name}/files/mark_delete", tags=["FILES"])
    async def mark_delete(self, app_name: str, UploadId: typing.Optional[str] = Body(...),
                          IsDelete: typing.Optional[bool] = Body(...)):
        """
        Danh dau xoa
        :param app_name:
        :param UploadId:
        :param IsDelete: True if mark deleted False if not
        :param token:
        :return:
        """
        doc_context = Repository.files.app(app_name).context
        delete_item = doc_context.context @ UploadId
        if delete_item is None:
            return {}
        doc_context.context.update(
            doc_context.fields.id == UploadId,
            doc_context.fields.MarkDelete << IsDelete
        )
        self.search_engine.mark_delete(app_name=app_name, id=UploadId, mark_delete_value=IsDelete)
        return dict()

    @controller.router.post("/api/{app_name}/files", tags=["FILES"])
    async def get_list(
            self,
            app_name: str,
            PageSize: int = Body(...),
            PageIndex: int = Body(...),
            FieldSearch: typing.Optional[str] = Body(default=None),
            ValueSearch: typing.Optional[str] = Body(default=None),
            DocType: typing.Optional[str] = Body(default="AllTypes")
    ):
        """
        Get list of file by tenant
        @param app_name: Tenant Name
        @param PageSize:
        @param PageIndex:
        @param FieldSearch:
        @param ValueSearch:
        @param DocType:
        @return:
        """

        try:
            items = self.file_service.get_list(
                app_name=app_name,
                root_url=cy_web.get_host_url(self.request),
                page_size=PageSize,
                page_index=PageIndex,
                field_search=FieldSearch,
                value_search=ValueSearch,
                doc_type=DocType

            )
            return [x.to_json_convertable() for x in items]
        except Exception as e:
            self.logger_service.error(e)
            return []

    @controller.router.post("/api/admin/files/move_tenant", tags=["FILES"])
    def move_tenant(self, data: typing.Optional[DataMoveTanentParam] = Body(...)):
        Data = data.Data
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

    @controller.router.post("/api/{app_name}/files/clone", tags=["FILES"])
    def clone_to_new(self,
                     app_name: str,
                     UploadId: typing.Annotated[str, Body(embed=True)]) -> CloneFileResult:

        item = self.file_service.do_copy(
            app_name=app_name,
            upload_id=UploadId,
            request=self.request
        )

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

    @controller.router.post("/api/{app_name}/files/delete", tags=["FILES"])
    async def files_delete(self, app_name: str,
                     UploadId: typing.Annotated[str, Body(embed=True)]) -> controller_model_files.DeleteFileResult:
        """
        This is not only delete physical file it is also delete file has been uploaded to cloud such as: Google Drive, One drive,...
        @param app_name:
        @param UploadId:
        @return:
        """
        file_path = await self.file_util_service.get_physical_path_async(
            app_name =app_name,
            upload_id= UploadId
        )




        if file_path and os.path.isfile(file_path):
            abs_dir = pathlib.Path(file_path).parent.__str__()

            import shutil

            try:
                if os.path.isdir(abs_dir):
                    shutil.rmtree(abs_dir,ignore_errors=True)
                    print(f"Directory '{abs_dir}' deleted successfully.")
            except OSError as e:
                print(f"Error deleting directory '{abs_dir}': {e}")

        upload_item = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.Id == UploadId
        )
        if upload_item is None:
            ret = controller_model_files.DeleteFileResult()
            ret.AffectedCount = 0
            return ret
        try:
            cloud_name, error = self.cloud_service_utils.get_cloud_name_of_upload(upload_item=upload_item)
            if error:
                ret = controller_model_files.DeleteFileResult()
                ret.Error = ErrorInfo()
                ret.Error.Code = error.get("Code")
                ret.Error.Message = error.get("Message")
                return ret
            if cloud_name != "local":
                ret, error = self.cloud_service_utils.drive_service.remove_upload(app_name=app_name, upload_id=UploadId,
                                                                                  cloud_name=cloud_name)
                if error:
                    ret = controller_model_files.DeleteFileResult()
                    ret.Error = ErrorInfo()
                    ret.Error.Code = error.get("Code")
                    ret.Error.Message = error.get("Message")
                    return ret
                # if not error:
                #     if cloud_name=="Google":
                #         if upload_item[Repository.files.fields.google_folder_path]:
                #             self.google_directory_service.delete_file(
                #                 app_name=app_name,
                #                 folder_path=upload_item[Repository.files.fields.google_folder_path],
                #                 filename= upload_item[Repository.files.fields.FileName]
                #             )
            affected_count = self.file_service.remove_upload(app_name=app_name, upload_id=UploadId)
            ret = controller_model_files.DeleteFileResult()
            ret.AffectedCount = affected_count
            Repository.files.app(app_name).context.delete(
                Repository.files.fields.Id == UploadId
            )
            return ret
        except Exception as e:
            ret = controller_model_files.DeleteFileResult()
            ret.Error = ErrorInfo()
            ret.Error.Code = "system"
            ret.Error.Message = repr(e)
            return ret

    @controller.router.post("/api/{app_name}/content/save", tags=["FILES"])
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
        data = args.data
        if not data.DocId or data.DocId == "":
            data.DocId = str(uuid.uuid4())

        data_item = self.file_service.get_upload_register(
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

    @controller.router.post("/api/{app_name}/files/content-re-process", tags=["FILES"])
    def file_content_re_process(
            self,
            app_name: str,
            UploadIds: typing.List[str] = Body(embed=True)):
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
