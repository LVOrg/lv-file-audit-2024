import typing

from cyx.common import config
import mimetypes
from enum import Enum
class ExtentProcess:
    name: str
    content_port: str
    image_port: str

    def __init__(self, name: str, content_port,image_port):
        self.name = name
        self.action_content = content_port
        self.action_image = image_port




def get_doc_type(file_ext: str) -> str:
    file_ext = file_ext.lower()
    mime_type, _ = mimetypes.guess_type(f"a.{file_ext}")
    if mime_type.startswith("image/"):
        return "image"
    elif file_ext.lower() == "pdf":
        return "pdf"
    elif mime_type.startswith("video/"):
        return "video"
    elif file_ext in config.ext_office_file:
        return "office"
    else:
        return "unknown"



