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
@cy_web.hanlder("post","{app_name}/layouts/detection")
def files_content_get_layout_detection_by_id(
        app_name: str,
        id:typing.Optional[str],
        token=fastapi.Depends(cy_xdoc.auths.Authenticate)):
    """
    This api get <br/>
    chỉ nhận nội dung tải lên theo id
    :param app_name:
    :param doc_id:
    :param data:
    :param token:
    :return:
    """
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    doc = search_engine.get_doc(
        app_name=app_name,
        id=id
    )
    if not doc:
        return None
    if not doc.source.doc_layout_analysis_data:
        return None
    if not doc.source.doc_layout_analysis_data.table:
        return None
    if not doc.source.doc_layout_analysis_data.table.table:
        return None
    else:
        return doc.source.doc_layout_analysis_data.table.table



