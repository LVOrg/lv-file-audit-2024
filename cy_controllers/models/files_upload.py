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
    Code: str
    Message: str
    Fields: typing.List[str]



class UploadFilesChunkInfoResult((BaseModel)):
    Data: typing.Optional[UploadChunkResult]
    Error: typing.Optional[ErrorResult]
