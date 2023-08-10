import typing
import cy_web
@cy_web.model()
class ErrorResult:
    Code:typing.Optional[str]
    Message:typing.Optional[str]
    Fields: typing.List[str]