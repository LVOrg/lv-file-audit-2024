import typing

import pydantic


class BullShitError(pydantic.BaseModel):
    code: typing.Optional[str]
    message: typing.Optional[str]
