import typing

import pydantic

from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError


class GetListFolderResult(pydantic.BaseModel):
    error: typing.Optional[BullShitError]
    data: typing.Optional[typing.List[dict]]
    total: typing.Optional[int]
class GetQuotaInfo(pydantic.BaseModel):
    remainingInBytes: typing.Optional[int]
    totalInBytes: typing.Optional[int]
    remainingInGB: typing.Optional[float]
    totalInGB: typing.Optional[float]
    driveType: typing.Optional[str]
class GetQuotaResult(pydantic.BaseModel):
    data: typing.Optional[GetQuotaInfo]
    error: typing.Optional[BullShitError]
class RegisterUploadResultInfo(pydantic.BaseModel):
    pass
class RegisterUploadResult(pydantic.BaseModel):
    data: typing.Optional[RegisterUploadResultInfo]
    error: typing.Optional[BullShitError]