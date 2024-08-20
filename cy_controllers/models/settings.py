import typing

import cy_docs
import datetime
import bson


class AISettings:
    Key: str
    Description: str
    CreatedOn: datetime.datetime
    ModifiedOn: datetime.datetime


class AIConfig:
    Gemini: AISettings
    GPT: AISettings


@cy_docs.define(
    name="LvFileServiceGlobalSettings"
)
class GlobalSettings:
    AI: AIConfig
