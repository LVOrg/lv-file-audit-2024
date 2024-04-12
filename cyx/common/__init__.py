import os.path
import pathlib

import cy_kit

config = cy_kit.yaml_config(os.path.join(
    pathlib.Path(__file__).parent.parent.parent.__str__(), "config.yml"
))

"""
All configs of File-Service was store here
"""
config_path = os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(), "config.yml")
"""
Path to location of config.yml
"""
import mimetypes
import pathlib


def get_doc_type(file_ext: str) -> str:
    file_ext = file_ext.lower()
    file_ext = pathlib.Path(file_ext).suffix
    if isinstance(file_ext, str) and file_ext[0] == ".":
        file_ext = file_ext[1:]
    else:
        return "unknown"
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
