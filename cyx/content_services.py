import enum
import pathlib
import typing
import mimetypes
from cyx.common import config


class ContentTypeEnum(enum.Enum):
    Video = 5
    Image = 4
    Office = 3
    Pdf = 1
    Unknown = 0


class ContentService:
    def __init__(self):
        pass

    def get_type(self, data: dict) -> ContentTypeEnum:
        ret = ContentTypeEnum.Unknown
        file_ext = data["FileExt"]
        if not file_ext:
            main_file_id = data["MainFileId"]
            if isinstance(main_file_id, str) and "://" in main_file_id:
                file_ext = pathlib.Path(main_file_id.splitlines("://")[1]).suffix
                if file_ext == "":
                    return ContentTypeEnum.Unknown
                else:
                    file_ext = file_ext[1:]
                    if file_ext == "pdf":
                        return ContentTypeEnum.Pdf
                    elif file_ext in config.ext_office_file:
                        return ContentTypeEnum.Office
                    elif file_ext == "avif":
                        return ContentTypeEnum.Image
                    else:
                        mt,_ = mimetypes.guess_type(f"a.{file_ext}")
                        if mt.startswith("image/"):
                            return ContentTypeEnum.Image
                        elif mt.startswith("video/"):
                            return ContentTypeEnum.Video

        elif file_ext == "pdf":
            return ContentTypeEnum.Pdf
        elif file_ext in config.ext_office_file:
            return ContentTypeEnum.Office
        elif file_ext == "avif":
            return ContentTypeEnum.Image
        else:
            mt, _ = mimetypes.guess_type(f"a.{file_ext}")
            if mt.startswith("image/"):
                return ContentTypeEnum.Image
            elif mt.startswith("video/"):
                return ContentTypeEnum.Video
        return ContentTypeEnum.Unknown