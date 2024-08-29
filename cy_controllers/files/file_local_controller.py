
import pathlib
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File
)
from starlette.responses import StreamingResponse
from cyx.common import config
import mimetypes
from typing import Annotated
router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
from cyx.repository import Repository
import os
from  cy_web.cy_web_x import streaming_async
import cy_file_cryptor.context
@controller.resource()
class FilesLocalController(BaseController):
    @controller.route.get(
        "/api/sys/admin/content-share/{rel_path:path}", summary="",
        response_class=StreamingResponse,
        tags=["LOCAL"]
    )
    async def read_raw_content_async(self,
                                      rel_path: str
                                      ) -> None:
        ret = await  self.read_raw_content_caller_async(rel_path)
        return ret
    async def read_raw_content_caller_async(self,
                               rel_path:str
                               ) -> None:

        check_file = os.path.join(config.file_storage_path, rel_path).replace('/', os.sep)
        if os.path.isfile(check_file):
            fs = open(check_file, "rb")
            content_type, _ = mimetypes.guess_type(check_file)
            ret = await streaming_async(
                fs, self.request, content_type, streaming_buffering=1024 * 4 * 3 * 8
            )
            ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return ret

        local_share_id= self.request.query_params.get("local-share-id")
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")

        upload_id = pathlib.Path(rel_path).parent.name.__str__()
        app_name = rel_path.split('/')[0]
        server_path = self.file_util_service.get_physical_path(app_name= app_name, upload_id=upload_id)


        if local_share_id:
            check_data = self.local_api_service.check_local_share_id(
                app_name=app_name,
                local_share_id=local_share_id
            )
            if check_data and isinstance(check_data.UploadId, str) and check_data.UploadId != upload_id:
                if not self.token_verifier.verify(self.share_key, token):
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="???")

        if os.path.isdir(f"{server_path}.chunks"):
            file_name= pathlib.Path(server_path).name.lower()
            return await self.file_util_service.get_file_content_async(self.request, app_name, f"{upload_id}/{file_name}")
        if not os.path.isfile(server_path):

            UploadData = await Repository.files.app(app_name).context.find_one_async(
                Repository.files.fields.id==upload_id
            )
            if UploadData is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            if UploadData.StorageType == "google-drive" and UploadData.CloudId:
                m, _ = mimetypes.guess_type(UploadData.FileName)
                return await self.g_drive_service.get_content_async(
                    app_name=app_name,
                    cloud_id=UploadData.CloudId,
                    client_file_name=UploadData.FileName,
                    request=self.request,
                    upload_id=upload_id,
                    content_type=m

                )
            if UploadData.StorageType == "onedrive" and UploadData.CloudId:
                m, _ = mimetypes.guess_type(UploadData.FileName)
                return await self.azure_utils_service.get_content_async(
                    app_name=app_name,
                    cloud_file_id=UploadData.CloudId,
                    content_type=m,
                    request=self.request,
                    upload_id=upload_id
                )
        else:
            fs = open(server_path, "rb")
            content_type, _ = mimetypes.guess_type(server_path)
            ret = await streaming_async(
                fs, self.request, content_type, streaming_buffering=1024 * 4 * 3 * 8
            )
            ret.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return ret

    @controller.route.post(
        "/api/sys/admin/content-write/{rel_path:path}", summary="",
        tags=["LOCAL"]
    )

    async def write_raw_content(self,rel_path: str,content: Annotated[UploadFile, File()]):
        local_share_id = self.request.query_params.get("local-share-id")
        token = self.request.query_params.get("token")
        is_ok = local_share_id or token
        if not is_ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="")

        server_path = os.path.join(self.config.file_storage_path, rel_path.replace('/', os.path.sep))
        server_dir = pathlib.Path(server_path).parent.__str__()
        os.makedirs(server_dir,exist_ok=True)
        file_size = content.size
        with open(server_path, 'wb',encrypt=True,file_size=file_size,chunk_size_in_kb=2048) as f:
            data_write = await content.read(2048)
            while data_write:
                f.write(data_write)
                data_write = await content.read(2048)
        return server_path


