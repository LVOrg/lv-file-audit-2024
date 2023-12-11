import typing


class DriverInfo:
    driveType:typing.Optional[str]
    ownerId: typing.Optional[str]
    ownerDisplayName:typing.Optional[str]
    remaining: typing.Optional[int]
    total: typing.Optional[int]

class ShareInfo:
    WebUrl: str
    AccessItem:str
    ContentUrl: str
    ShareId: str
    Id:str