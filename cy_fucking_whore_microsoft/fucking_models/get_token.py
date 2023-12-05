import typing

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError
import pydantic


class GetTokenResult(pydantic.BaseModel):
    token: typing.Optional[str]
    scopes: typing.Optional[typing.List[str]]
    error: typing.Optional[BullShitError]
