import enum
import os.path
import pathlib
import typing
import mimetypes

import cy_docs
import cyx.common.msg
from cyx.common import config


class ContentTypeEnum(enum.Enum):
    Video = 5
    Image = 4
    Office = 3
    Pdf = 1
    Unknown = 0


from cyx.common import config


class ContentService:
    def __init__(self):
        self.file_storage_path = config.file_storage_path

    def get_type(self, msg_data: typing.Union[dict, cy_docs.DocumentObject]) -> ContentTypeEnum:
        data = msg_data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
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
                        mt, _ = mimetypes.guess_type(f"a.{file_ext}")
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

    def get_master_resource(self, msg_info: cyx.common.msg.MessageInfo):
        data = msg_info.Data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
        main_file_id = data["MainFileId"]
        if isinstance(main_file_id, str) and "://" in main_file_id:
            rel_path = main_file_id.split("://")[1]
            real_file_path = os.path.join(self.file_storage_path, rel_path)
            return real_file_path
        return None

    def get_resource(self, msg_info: cyx.common.msg.MessageInfo):
        if isinstance(msg_info.resource, str):
            return msg_info.resource
        data = msg_info.Data
        if isinstance(data, cy_docs.DocumentObject):
            data = data.to_json_convertable()
        main_file_id = data["MainFileId"]
        if isinstance(main_file_id, str) and "://" in main_file_id:
            rel_path = main_file_id.split("://")[1]
            real_file_path = os.path.join(self.file_storage_path, rel_path)
            return real_file_path
        return None
