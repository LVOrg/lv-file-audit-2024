from cy_fucking_pnp_wopi.models.wopi import WopiAction
import datetime
import typing
import uuid


class FileModel:
    id: uuid.UUID
    LockValue: str
    LockExpires: typing.Optional[datetime.datetime]
    OwnerId: str
    BaseFileName: str
    Container: str
    Size: int
    Version: int
    UserInfo: str


class DetailedFileModel(FileModel):
    UserId: str
    CloseUrl: str
    HostEditUrl: str
    HostViewUrl: str
    SupportsCoauth: bool = False
    SupportsExtendedLockLength: bool = False
    SupportsFileCreation: bool = False
    SupportsFolders: bool = False
    SupportsGetLock: bool = True
    SupportsLocks: bool = True
    SupportsRename: bool = True
    SupportsScenarioLinks: bool = False
    SupportsSecureStore: bool = False
    SupportsUpdate: bool = True
    SupportsUserInfo: bool = True
    LicensesCheckForEditIsEnabled: bool = True

    ReadOnly: bool = False
    RestrictedWebViewOnly: bool = False
    UserCanAttend: bool = False  # Broadcast only
    UserCanNotWriteRelative: bool = False
    UserCanPresent: bool = False  # Broadcast only
    UserCanRename: bool = True
    UserCanWrite: bool = True
    WebEditingDisabled: bool = False

    Actions: typing.List[WopiAction]