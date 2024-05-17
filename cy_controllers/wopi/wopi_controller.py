
"""
This pakage is refer to https://github.com/OfficeDev/PnP-WOPI/tree/master
https://learn.microsoft.com/en-us/openspecs/office_protocols/ms-wopi/0f0bf842-6353-49ed-91c0-c9d672f21200
"""
import pathlib

from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
    responses
)

from cy_xdoc.auths import Authenticate
import hashlib
import base64
import os
router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.wopi_models import WopiFileInfo

WOPI_FILE_DIR = pathlib.Path(__file__).parent.parent.parent.__str__()

@controller.resource()
class WOPIController(BaseController):
    # dependencies = [
    #     Depends(Authenticate)
    # ]

    def __init__(self, request: Request):
        self.request = request


    async def __wopi_get_file_async__(self, app_name:str,fileid:str,access_token: str  ) -> WopiFileInfo:
        """
        Get file info. Implements the CheckFileInfo WOPI call
        The fucking Microsoft said "The CheckFileInfo operation
        is one of the most important WOPI operations. CheckFileInfo must be implemented for all WOPI actions. This
        operation returns information about a file, a user’s permissions on that file, and general information about
        the capabilities that the WOPI host has on the file. Also, some CheckFileInfo properties can influence the
        appearance and behavior of WOPI clients."
        :param app_name:
        :param fileid: A File ID is a string that represents a file or folder being operated on by way of WOPI operations.
                       A host must issue a unique ID for any file used by a WOPI client.
                       The client will then include the file ID when making requests to the WOPI host.
                       So, a host must be able to use the file ID to locate a particular file
        :return:
        """
        '''Get file info. Implements the CheckFileInfo WOPI call'''
        print('Get file info. Implements the CheckFileInfo WOPI call')
        fileid = fileid.split('.')[0]
        upload_info = self.file_service.get_upload_register(
            app_name=app_name,
            upload_id=fileid
        )
        fs = self.file_storage_service.get_file_by_id(
            app_name=app_name, id=upload_info.MainFileId
        )

        # file_path = os.path.join(WOPI_FILE_DIR, fileid)
        # rf = open(file_path, 'rb')
        file_size = fs.get_size()
        f = await fs.read(file_size)
        ret = WopiFileInfo()
        ret.BaseFileName = fileid
        ret.OwnerId = 'qi'
        ret.Size = file_size
        dig = hashlib.sha256(f).digest()
        ret.SHA256 = base64.b64encode(dig).decode()

        ret.Version = '1'
        ret.SupportsUpdate = True
        ret.UserCanWrite = True
        ret.SupportsLocks  = True
        return ret

    @controller.route.get(
        "/api/{app_name}/wopi/files/{fileid}", summary="Re run index search",
        tags=["WOPI"]
    )
    async def wopi_get_file(self, app_name: str, fileid: str) :
        return {"file_content": "dadada"}
        # return await self.__wopi_get_file_async__(app_name,fileid,access_token)
    @controller.route.post(
        "/api/{app_name}/wopi/files/{fileid}", summary="Re run index search",
        tags=["WOPI"]
    )
    async def wopi_get_file_post(self, app_name: str, fileid: str) :
        return await self.__wopi_get_file_async__(app_name,fileid,access_token)

    async def __wopi_get_file_content_async__(self, app_name: str, fileid: str):
        '''Request to file contents, Implements the GetFile WOPI call'''
        fileid = fileid.split('.')[0]
        upload_info = self.file_service.get_upload_register(
            app_name=app_name,
            upload_id=fileid
        )
        fs = self.file_storage_service.get_file_by_id(
            app_name=app_name, id=upload_info.MainFileId
        )

        async def get_file_stream(_fs):
            chunk_size = 8192
            while data := await fs.read(chunk_size):
                yield data

        print('get file contents')

        response = responses.StreamingResponse(
            content=get_file_stream(fs)

        )
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileid)
        return response

    @controller.route.get(
        "/api/{app_name}/wopi/files/{fileid}/contents", summary="Re run index search",
        tags=["WOPI"]
    )
    async def wopi_get_file_content(self, app_name: str, fileid: str):
        return await self.__wopi_get_file_content_async__(
            app_name=app_name,
            fileid=fileid
        )
    @controller.route.post(
        "/api/{app_name}/wopi/files/{fileid}/contents", summary="Re run index search",
        tags=["WOPI"]
    )
    async def wopi_save_file_content(self, app_name: str, fileid: str):
        print('Update file with new contents. Implements the PutFile WOPI call')
        data  = await self.request.body()
        print(data)
