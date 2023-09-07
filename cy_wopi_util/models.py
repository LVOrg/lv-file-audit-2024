import typing
from datetime import datetime

class WopiAction:
    """
    A WOPI action.

    Attributes:
        app: The name of the application that the action belongs to.
        favIconUrl: The URL of the application's favorite icon.
        checkLicense: Whether the action requires a license to be checked.
        name: The name of the action.
        ext: The file extension that the action supports.
        progid: The progid for the action.
        requires: The capabilities that the action requires.
        isDefault: Whether the action is the default action for the file extension.
        urlsrc: The URL of the action.
    """

    app: str
    favIconUrl: str
    checkLicense: bool
    name: str
    ext: str
    progid: str
    requires: str
    isDefault: typing.Optional[bool]
    urlsrc: str

class FileModel:
    """
    A file in a WOPI store.

    Attributes:
        id: The ID of the file.
        LockValue: The value of the lock, if the file is locked.
        LockExpires: The date and time when the lock expires, if the file is locked.
        OwnerId: The ID of the user who owns the file.
        BaseFileName: The base file name of the file.
        Container: The container that the file belongs to.
        Size: The size of the file in bytes.
        Version: The version of the file.
        UserInfo: The user information for the file.
    """

    id: str
    LockValue: str
    LockExpires: typing.Optional[datetime]
    OwnerId: str
    BaseFileName: str
    Container: str
    Size: int
    Version: int
    UserInfo: str


class DetailedFileModel(FileModel):
    """
    Detailed information about a file.

    Attributes:
        UserId: The ID of the user who owns the file.
        CloseUrl: The URL to close the file.
        HostEditUrl: The URL to edit the file in the WOPI host.
        HostViewUrl: The URL to view the file in the WOPI host.
        SupportsCoauth: Whether the file supports coauthoring.
        SupportsExtendedLockLength: Whether the file supports extended lock lengths.
        SupportsFileCreation: Whether the file supports file creation.
        SupportsFolders: Whether the file supports folders.
        SupportsGetLock: Whether the file supports getting a lock.
        SupportsLocks: Whether the file supports locks.
        SupportsRename: Whether the file supports renaming.
        SupportsScenarioLinks: Whether the file supports scenario links.
        SupportsSecureStore: Whether the file supports the secure store.
        SupportsUpdate: Whether the file supports updating.
        SupportsUserInfo: Whether the file supports user information.
        LicensesCheckForEditIsEnabled: Whether licenses are checked for editing.
        ReadOnly: Whether the file is read-only.
        RestrictedWebViewOnly: Whether the file can only be viewed in a restricted web view.
        UserCanAttend: Whether the user can attend a broadcast.
        UserCanNotWriteRelative: Whether the user cannot write relative to the file.
        UserCanPresent: Whether the user can present a broadcast.
        UserCanRename: Whether the user can rename the file.
        UserCanWrite: Whether the user can write to the file.
        WebEditingDisabled: Whether web editing is disabled for the file.
        Actions: A list of WOPI actions that are supported for the file.
    """

    UserId: str
    CloseUrl: str
    HostEditUrl: str
    HostViewUrl: str
    SupportsCoauth: bool
    SupportsExtendedLockLength: bool
    SupportsFileCreation: bool
    SupportsFolders: bool
    SupportsGetLock: bool
    SupportsLocks: bool
    SupportsRename: bool
    SupportsScenarioLinks: bool
    SupportsSecureStore: bool
    SupportsUpdate: bool
    SupportsUserInfo: bool
    LicensesCheckForEditIsEnabled: bool
    ReadOnly: bool
    RestrictedWebViewOnly: bool
    UserCanAttend: bool
    UserCanNotWriteRelative: bool
    UserCanPresent: bool
    UserCanRename: bool
    UserCanWrite: bool
    WebEditingDisabled: bool
    Actions: typing.List[WopiAction]
