import datetime
import typing

import cy_web


@cy_web.model(all_fields_are_optional=True)
class FileUploadRegisterInfo:
    UploadId:str
    FileName:str
    Status:int
    SizeInHumanReadable:str
    ServerFileName:str
    IsPublic:bool
    FullFileName:str
    MimeType:str
    FileSize:int
    UploadId:str
    CreatedOn:datetime.datetime
    FileNameOnly:str
    UrlOfServerPath:str
    """
    Abs url for content accessing
    http://172.16.1.210:8011/api/lv-test/file/22bd557d-e78f-4157-a735-2d95fc64d302/story_content/story.js
    """
    AppName:str
    RelUrlOfServerPath:str
    """
    Relative url for content processing
    The fucking looks like this /lv-test/file/22bd557d-e78f-4157-a735-2d95fc64d302/story_content/story.js
    """
    ThumbUrl:str
    """
    The fucking main thumb look like
    http://172.16.1.210:8011/api/lv-test/thumb/0048135e-50e5-4f56-8c89-b2f8fe83b06b/story.js.webp
    """
    AvailableThumbs:typing.List[str]
    Media: typing.Optional[dict]
    HasThumb:bool
    OcrContentUrl:str
    OCRFileId:str