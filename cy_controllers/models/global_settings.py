import datetime

from pydantic import BaseModel
import typing


class APIKeyInfo(BaseModel):
    Key: str | None
    Description: str | None
    # CreatedOn: datetime.datetime | None
    # ModifiedOn: datetime.datetime | None

class AIConfigModel(BaseModel):
    Gemini: typing.Optional[APIKeyInfo]
    GPT: typing.Optional[APIKeyInfo]
class SettingInfo(BaseModel):
    AIConfig: AIConfigModel
