import pathlib

from cyx.common import config
from mimetypes import guess_type


def check_is_thumbnails_able(doc_item):
    if doc_item is None:
        return False
    if doc_item.Status!=1:
        return False
    if doc_item.ThumbnailsAble:
        return doc_item.ThumbnailsAble
    if doc_item.FileExt in config.ext_office_file:
        return True
    if pathlib.Path(doc_item.FileName).suffix[1:] in config.ext_office_file:
        return True
    if doc_item.FileName:
        t, _ = guess_type(doc_item.FileName)
        if t.startswith("video/"):
            return True
        if t.startswith("image/"):
            return True
    return False
