"""
Hiển thị nội dung OCR của file ảnh
"""
import typing
import uuid
from datetime import datetime

import fastapi
import cy_xdoc.auths
import cy_web
import cy_xdoc
import mimetypes
import cy_kit
import cy_xdoc.services.files
from cy_xdoc.services.search_engine import SearchEngine
import cyx.common.file_storage
from cy_xdoc.models.files import DocUploadRegister
from cy_xdoc.controllers.models.files_register import FileContentSaveData,FileContentSaveResult,PrivilegesType

search_engine = cy_kit.singleton(SearchEngine)
file_service = cy_kit.singleton(cy_xdoc.services.files.FileServices)
from typing import Optional, List
# @cy_web.hanlder("post","{app_name}/content/save")
# def test(app_name:str,doc_id:str):
#     pass


@cy_web.hanlder("post","{app_name}/content/update_by_conditional")
def file_content_update_by_conditional(
        app_name: str,
        conditional:dict,
        data_update:dict,
        token=fastapi.Depends(cy_xdoc.auths.Authenticate)):
    """
    Update data to search engine with conditional<br/>
    Cập nhật dữ liệu lên công cụ tìm kiếm có điều kiện
    :param app_name:
    :param doc_id:
    :param data:
    :param token:
    :return:
    """
    ret = search_engine.update_by_conditional(
        app_name = app_name,
        conditional= conditional,
        data = data_update
    )
    return  ret

