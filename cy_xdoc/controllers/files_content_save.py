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
@cy_web.hanlder("post","{app_name}/content/save")
def file_content_save(
        app_name: str,
        data:FileContentSaveData,
        token=fastapi.Depends(cy_xdoc.auths.Authenticate)):
    """
    Insert or update more data to UploadRegister<br/>
    Chèn hoặc cập nhật thêm dữ liệu vào UploadRegister
    :param app_name:
    :param doc_id:
    :param data:
    :param token:
    :return:
    """
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    if not data.DocId  or data.DocId == "":
        data.DocId = str(uuid.uuid4())

    data_item= file_service.get_upload_register(
        app_name = app_name,
        upload_id= data.DocId,

    )
    if data_item and data.Privileges:
        json_privilege = {}
        for x in data.Privileges or []:
            if json_privilege.get(x.Type.lower()):
                json_privilege[x.Type.lower()] += x.Values.split(',')
            else:
                json_privilege[x.Type.lower()] = x.Values.split(',')
        data_item["Privileges"] = json_privilege
    else:
        _source = search_engine.get_doc(
            app_name=app_name,
            id=data.DocId
        )
        _source_data_item = None
        if _source:
            _source_data_item=_source.source.data_item
        fx= DocUploadRegister()


        json_privilege = {}
        for x in data.Privileges or []:
            if json_privilege.get(x.Type.lower()):
                json_privilege[x.Type.lower()] += x.Values.split(',')
            else:
                json_privilege[x.Type.lower()]=x.Values.split(',')

        data_item = _source_data_item or {
            "FileName":"Unknown",
            "Status":1,
            "MarkDelete":False,
            "RegisterOn":datetime.utcnow(),
            "_id":data.DocId,
            "SizeInBytes":0,
            "Privileges":json_privilege
        }
        if data.Privileges is not None:
            data_item["Privileges"] = json_privilege

    search_engine.update_content(
        app_name=app_name,
        content=data.Content,
        data_item= data_item,
        meta_info = data.MetaData,
        id= data.DocId,
        replace_content=True
    )
    data_item["Id"] = data.DocId
    import cy_docs
    return data_item.to_json_convertable() if isinstance(data_item,cy_docs.DocumentObject) else data_item

