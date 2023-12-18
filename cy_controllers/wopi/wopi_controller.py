
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

    @controller.route.get(
        "/api/{app_name}/wopi/files/{fileid}", summary="Re run index search"
    )
    @controller.route.get(
        "/api/{app_name}/wopi/files/{fileid}", summary="Re run index search"
    )
    def wopi_get_file(self, app_name:str,fileid:str) -> WopiFileInfo:
        """
        Get file info. Implements the CheckFileInfo WOPI call
        :param app_name:
        :param fileid:
        :return:
        """
        '''Get file info. Implements the CheckFileInfo WOPI call'''
        print('Get file info. Implements the CheckFileInfo WOPI call')
        file_path = os.path.join(WOPI_FILE_DIR, fileid)
        rf = open(file_path, 'rb')
        f = rf.read()
        ret = WopiFileInfo()
        ret.BaseFileName = fileid
        ret.OwnerId = 'qi'
        ret.Size = len(f)
        dig = hashlib.sha256(f).digest()
        ret.SHA256 = base64.b64encode(dig).decode()

        ret.Version = '1'
        ret.SupportsUpdate = True
        ret.UserCanWrite = True
        ret.SupportsLocks  = True
        return ret

    @controller.route.post(
        "/api/{app_name}/wopi/files/{fileid}", summary="Re run index search"
    )
    def wopi_get_file(self, app_name: str, fileid: str) -> WopiFileInfo:
        """
        Get file info. Implements the CheckFileInfo WOPI call
        :param app_name:
        :param fileid:
        :return:
        """
        '''Get file info. Implements the CheckFileInfo WOPI call'''
        print('Get file info. Implements the CheckFileInfo WOPI call')
        file_path = os.path.join(WOPI_FILE_DIR, fileid)
        rf = open(file_path, 'rb')
        f = rf.read()
        ret = WopiFileInfo()
        ret.BaseFileName = fileid
        ret.OwnerId = 'qi'
        ret.Size = len(f)
        dig = hashlib.sha256(f).digest()
        ret.SHA256 = base64.b64encode(dig).decode()

        ret.Version = '1'
        ret.SupportsUpdate = True
        ret.UserCanWrite = True
        ret.SupportsLocks = True
        return ret
    @controller.route.get(
        "/api/{app_name}/wopi/files/{fileid}/contents", summary="Re run index search"
    )
    def wopi_get_file_content(self, app_name: str, fileid: str):
        '''Request to file contents, Implements the GetFile WOPI call'''
        print('Request to file contents, Implements the GetFile WOPI call')
        file_path = os.path.join(WOPI_FILE_DIR, fileid)

        def get_file_stream(file_path):
            with file_path.open("rb") as f:
                chunk_size = 8192
                while data := f.read(chunk_size):
                    yield data
        print('get file contents')

        response = responses.StreamingResponse(
            content=get_file_stream(file_path)

        )
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileid)
        return response

    @controller.route.post(
        "/api/{app_name}/wopi/files/{fileid}/contents", summary="Re run index search"
    )
    async def wopi_save_file_content(self, app_name: str, fileid: str):
        print('Update file with new contents. Implements the PutFile WOPI call')
        data  = await self.request.body()
        print(data)
