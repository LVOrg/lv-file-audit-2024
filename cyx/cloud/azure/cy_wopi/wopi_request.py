"""
public static WopiRequest ParseRequest(HttpRequest request)
"""
import typing

import fastapi.requests
from enum import Enum
from cy_wopi import (
    wopi_utils, wopi_request_headers)

class WopiRequestType(Enum):
    Unknown = -1
    NUll = 0
    CheckFileInfo = 1
    GetFile = 2
    Lock = 3
    GetLock = 4
    RefreshLock = 5
    Unlock = 6
    UnlockAndRelock = 7
    PutFile = 8
    PutRelativeFile = 9
    RenameFile = 10
    PutUserInfo = 11

    DeleteFile = 12  # ONENOTE ONLY
    ExecuteCellStorageRequest = 13  # ONENOTE ONLY
    ExecuteCellStorageRelativeRequest = 14  # ONENOTE ONLY
    ReadSecureStore = 15  # NO DOCS
    GetRestrictedLink = 16  # NO DOCS
    RevokeRestrictedLink = 17  # NO DOCS
    ExecuteCobaltRequest = 18  # In GitHub Sample
    CheckFolderInfo = 19  # In GitHub Sample
    EnumerateChildren = 20  # In GitHub Sample
WopiRequestTypeMapper = dict(
    GET_LOCK = WopiRequestType.GetLock,
    REFRESH_LOCK = WopiRequestType.RefreshLock,
    UNLOCK = WopiRequestType.Unlock,
    LOCK = WopiRequestType.UnlockAndRelock,
    PUT_RELATIVE=WopiRequestType.PutRelativeFile,
    RENAME_FILE =  WopiRequestType.RenameFile,
    PUT_USER_INFO = WopiRequestType.PutUserInfo,
    DELETE = WopiRequestType.DeleteFile,
    READ_SECURE_STORE = WopiRequestType.ReadSecureStore,
    GET_RESTRICTED_LINK = WopiRequestType.GetRestrictedLink,
    REVOKE_RESTRICTED_LINK = WopiRequestType.RevokeRestrictedLink,
    COBALT = WopiRequestType.ExecuteCobaltRequest,
    CHECK_INFO = WopiRequestType.CheckFolderInfo
)
class WopiRequest:
    id: typing.Optional[str]
    request_type: typing.Optional[WopiRequestType]
    access_token: typing.Optional[str]


def parse_request(request:fastapi.requests.Request)->typing.Optional[WopiRequest]:
    request_data = WopiRequest()
    request_data.request_type = WopiRequestType.NUll
    request_data.access_token = request.query_params.get("access_token")
    request_data.id = ""
    request_path = request.url.path.lower() # get absolute url of request
    position_of_base_path = request_path.index(wopi_utils.WOPI_BASE_PATH)+len(wopi_utils.WOPI_BASE_PATH)
    wopi_path = request_path[position_of_base_path:]
    if wopi_path.startswith(wopi_utils.WOPI_FILES_PATH):
        raw_id = wopi_path[len(wopi_utils.WOPI_FILES_PATH):]
        if raw_id.endswith(wopi_utils.WOPI_CONTENTS_PATH):
            # The rawId ends with /contents so this is a request to read/write the file contents

            # Remove /contents from the end of rawId to get the actual file id
            request_data.id = raw_id[:-len(wopi_utils.WOPI_CONTENTS_PATH)]

            # Check request verb to determine file operation
            if request.method == "GET":
                request_data.request_type = WopiRequestType.GetFile
            elif request.method == "POST":
                request_data.request_type = WopiRequestType.PutFile
        else:
            request_data.id = raw_id
            if request.method == "GET":
                # GET requests to the file are always CheckFileInfo
                request_data.request_type = WopiRequestType.CheckFileInfo
            elif request.method == "POST":
                # Use the X-WOPI-Override header to determine the request type for POSTs
                wopi_override = request.headers.get(wopi_request_headers.OVERRIDE)
                request_data.request_type = WopiRequestType.Unknown
                request_data.request_type = WopiRequestTypeMapper.get(wopi_override, WopiRequestType.Unknown)
    elif wopi_path.startswith(wopi_utils.WOPI_FOLDERS_PATH):
        raw_id = wopi_path[len(wopi_utils.WOPI_FOLDERS_PATH):]

        if raw_id.endswith(wopi_utils.WOPI_CHILDREN_PATH):
            # rawId ends with /children, so it's an EnumerateChildren request.

            # Remove /children from the end of rawId
            request_data.id = raw_id[:-len(wopi_utils.WOPI_CHILDREN_PATH)]
            # request_data.request_type = WopiRequestType.EnumerateChildren
        else:
            # rawId doesn't end with /children, so it's a CheckFolderInfo.

            request_data.id = raw_id
            # request_data.request_type = WopiRequestType.CheckFolderInfo

    else:
        request_data.request_type = WopiRequestType.NUll
    return request_data

