import typing


class WopiAction:
    app: str
    fav_icon_url: str
    check_license: bool
    name: str
    ext: str
    progid: str
    requires: str
    is_default: typing.Optional[bool]
    urlsrc: str


class WopiProof:
    old_value: str
    old_modulus: str
    old_exponent: str
    value: str
    modulus: str
    exponent: str


from enum import Enum


class WopiRequestType(Enum):
    NONE = 0
    CHECK_FILE_INFO = 1
    GET_FILE = 2
    LOCK = 3
    GET_LOCK = 4
    REFRESH_LOCK = 5
    UNLOCK = 6
    UNLOCK_AND_RELOCK = 7
    PUT_FILE = 8
    PUT_RELATIVE_FILE = 9
    RENAME_FILE = 10
    PUT_USER_INFO = 11

    # ONENOTE ONLY
    # DELETE_FILE = 12
    # EXECUTE_CELL_STORAGE_REQUEST = 13
    # EXECUTE_CELL_STORAGE_RELATIVE_REQUEST = 14

    # NO DOCS
    # READ_SECURE_STORE = 15
    # GET_RESTRICTED_LINK = 16
    # REVOKE_RESTRICTED_LINK = 17

    # GitHub Sample
    # EXECUTE_COBALT_REQUEST = 18
    # CHECK_FOLDER_INFO = 19
    # ENUMERATE_CHILDREN = 20


class WopiRequest:
    Id: str
    RequestType: WopiRequestType
    AccessToken: str
