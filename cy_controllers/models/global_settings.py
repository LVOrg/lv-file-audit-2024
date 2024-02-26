import datetime

from pydantic import BaseModel
import typing


class APIKeyInfo(BaseModel):
    Key: str | None
    Description: str | None
    CreatedOn: datetime.datetime | None
    ModifiedOn: datetime.datetime | None


class SettingInfo(BaseModel):
    AI: typing.Optional[APIKeyInfo]
