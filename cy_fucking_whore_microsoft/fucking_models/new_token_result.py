import typing

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError
import pydantic


class AcquireNewToken(pydantic.BaseModel):
    token: typing.Optional[str]
    scope: typing.Optional[str]


class AcquireNewTokenResult(pydantic.BaseModel):
    tokenInfo: typing.Optional[AcquireNewToken]
    error: typing.Optional[BullShitError]
