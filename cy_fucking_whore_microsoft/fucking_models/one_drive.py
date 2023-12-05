import typing

import pydantic

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError


class GetListFolderResult(pydantic.BaseModel):
    error: typing.Optional[BullShitError]
    data: typing.Optional[typing.List[dict]]
    total: typing.Optional[int]
