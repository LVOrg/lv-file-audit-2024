import datetime
import os
import sys

import pathlib

sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import typing
import uuid

import elasticsearch

import cy_file_cryptor.wrappers
import cy_docs
from cyx.repository import Repository
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common import config
import cyx.common.msg
import cy_kit
from cyx.local_api_services import LocalAPIService
from cyx.lv_ocr_services import LVOCRService
from cy_utils import texts
from cy_xdoc.services.search_engine import SearchEngine
import cy_utils

local_api_service = cy_kit.singleton(LocalAPIService)
lv_ocr_service = cy_kit.singleton(LVOCRService)
msg = cy_kit.singleton(RabitmqMsg)
apps = Repository.apps.app("admin").context.find({})
finish = dict()
_apps = list(apps)
# for app in _apps:
#     Repository.files.app(app.Name).context.update(
#         {},
#         Repository.files.fields.ProcessInfo <<None
#     )
filter = Repository.files.fields.FileExt == "pdf"
filter = filter | (Repository.files.fields.MimeType.startswith("image/"))
filter = filter & (Repository.files.fields.IsLvOrc3 == None)
from cyx.file_process_mapping import get_doc_type

search_engine = cy_kit.singleton(SearchEngine)


def get_docs_miss_msg(app_name: str, action_type: str | None = None, limit=10):
    filter_info = Repository.files.fields.ProcessInfo == None
    if action_type is not None:
        filter_msg = getattr(Repository.files.fields.ProcessInfo, action_type) == None
        filter = filter_info | filter_msg
    else:
        filter = filter_info
    context = Repository.files.app(app_name).context
    arg = context.aggregate().match(
        filter
    ).sort(
        Repository.files.fields.RegisterOn.desc()
    ).limit(limit)

    ret = list(arg)
    return ret


while True:
    apps = Repository.apps.app("admin").context.find({})
    finish = dict()
    _apps = list(apps)
    action_keys = ["content", "image"]

    for app in _apps:
        for action_key in action_keys:
            files_context = Repository.files.app(app.Name)
            files = get_docs_miss_msg(app.Name, action_key)
            for file in files:
                file_ext = file[Repository.files.fields.FileExt]
                if file_ext is None:
                    file_ext = pathlib.Path(file[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
                doc_type = get_doc_type(file_ext)
                if hasattr(config.process_services, doc_type):
                    try:
                        download_url, rel_path, download_file, token,share_id = local_api_service.get_download_path(file, app.Name)

                        action_info = getattr(config.process_services, doc_type)
                        content = "\n"
                        if hasattr(action_info, action_key):
                            try:
                                content = cy_utils.run_action(
                                    action=getattr(action_info, action_key),
                                    url_file=download_url,
                                    action_type=action_key,
                                    download_file=download_file
                                )
                            except NotImplemented as ex:
                                raise ex
                            content = cy_utils.texts.well_form_text(content)
                        if action_key == "content":
                            search_engine.update_content(
                                app_name=app.Name,
                                id=file.id,
                                content=content,
                                replace_content=True
                            )
                        else:
                            local_api_service.send_file(
                                file_path=content,
                                token=token,
                                local_share_id=share_id,
                                app_name= app.Name,
                                rel_server_path=rel_path

                            )
                        if file[files_context.fields.ProcessInfo] is None:
                            files_context.context.update(
                                files_context.fields.id == file.id,
                                files_context.fields.ProcessInfo << {action_key: dict(

                                    IsError=False,
                                    Error="",
                                    UpdateTime=datetime.datetime.utcnow(),

                                )}
                            )
                        else:
                            files_context.context.update(
                                files_context.fields.id == file.id,
                                getattr(files_context.fields.ProcessInfo, action_key) << dict(
                                    IsError=False,
                                    Error="",
                                    UpdateTime=datetime.datetime.utcnow(),

                                )
                            )
                    except Exception as ex:
                        if file[files_context.fields.ProcessInfo] is None:
                            files_context.context.update(
                                files_context.fields.id == file.id,
                                files_context.fields.ProcessInfo << {action_key: dict(

                                    IsError=True,
                                    Error=str(ex),
                                    UpdateTime=datetime.datetime.utcnow(),

                                )}
                            )
                        else:
                            files_context.context.update(
                                files_context.fields.id == file.id,
                                getattr(files_context.fields.ProcessInfo, action_key) << dict(
                                    IsError=True,
                                    Error=str(ex),
                                    UpdateTime=datetime.datetime.utcnow(),

                                )
                            )
