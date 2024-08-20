import typing
import cy_web
from pydantic import BaseModel
class ErrorResult(BaseModel):
    Code:typing.Optional[str]
    Message:typing.Optional[str]
    Fields: typing.List[str]