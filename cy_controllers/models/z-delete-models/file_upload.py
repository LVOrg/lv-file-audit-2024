import typing

import cy_web


@cy_web.model()
class UploadChunkResult:
    SizeInHumanReadable: str
    SizeUploadedInHumanReadable: str
    Percent: float
    NumOfChunksCompleted: int


@cy_web.model()
class Error:
    """
    Thông tin chi tiết của lỗi
    """
    Code: str
    Message: str
    Fields: typing.List[str]


@cy_web.model()
class UploadFilesChunkInfoResult:
    Data: typing.Optional[UploadChunkResult]
    Error: typing.Optional[Error]
