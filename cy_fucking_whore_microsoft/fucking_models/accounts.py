import typing

import pydantic

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError


class InviteUserResult(pydantic.BaseModel):
    error: typing.Optional[BullShitError]
    data: typing.Optional[dict]
