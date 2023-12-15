import typing

import pydantic


class WopiFileInfo(pydantic.BaseModel):
    BaseFileName: typing.Optional[str]
    OwnerId: str | None
    Size: int | None
    SHA256: str | None
    Version: str | None
    SupportsUpdate: bool | None
    UserCanWrite: bool | None
    SupportsLocks: bool | None
