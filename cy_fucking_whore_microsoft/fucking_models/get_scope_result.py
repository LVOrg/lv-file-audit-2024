import typing

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError
import pydantic
class ScopeInfo(pydantic.BaseModel):
    name: str
    description : typing.Optional[str]

class ScopesInfoResult(pydantic.BaseModel):
    scopes: typing.Optional[typing.List[ScopeInfo]]
    error : typing.Optional[BullShitError]
