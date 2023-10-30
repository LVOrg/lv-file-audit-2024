from pydantic import BaseModel
import typing
class UploadChunkResult(BaseModel):
    SizeInHumanReadable: typing.Optional[str]
    SizeUploadedInHumanReadable: typing.Optional[str]
    Percent: typing.Optional[float]
    NumOfChunksCompleted: typing.Optional[int]



class ErrorResult(BaseModel):
    """
    Thông tin chi tiết của lỗi
    """
    Code: typing.Optional[str]
    Message: typing.Optional[str]
    Fields: typing.Optional[typing.List[str]]



class UploadFilesChunkInfoResult((BaseModel)):
    Data: typing.Optional[UploadChunkResult]
    Error: typing.Optional[ErrorResult]
