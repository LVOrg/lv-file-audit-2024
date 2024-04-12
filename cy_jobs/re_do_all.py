import datetime
import os
import sys

import pathlib
from itertools import accumulate

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
from gradio_client import Client
local_api_service = cy_kit.singleton(LocalAPIService)
lv_ocr_service = cy_kit.singleton(LVOCRService)
msg = cy_kit.singleton(RabitmqMsg)
apps = Repository.apps.app("admin").context.find(Repository.apps.fields.Name=="lv-docs")
finish = dict()
_apps = list(apps)
for app in _apps:
    Repository.files.app(app.Name).context.update(
        {},
        Repository.files.fields.ProcessInfo <<None
    )
filter = Repository.files.fields.FileExt == "pdf"
filter = filter | (Repository.files.fields.MimeType.startswith("image/"))
filter = filter & (Repository.files.fields.IsLvOrc3 == None)
from cyx.file_process_mapping import get_doc_type
process_services_host = config.process_services_host or "http://localhost"
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
    apps = Repository.apps.app("admin").context.aggregate().sort(
        Repository.apps.fields.LatestAccess.desc()
    )

    finish = dict()
    _apps = list(apps)
    action_keys = ["content", "image"]

    for app in _apps:
        for action_key in action_keys:
            files_context = Repository.files.app(app.Name)
            files = get_docs_miss_msg(app.Name, action_key,limit=5)
            for file in files:
                file_ext = file[Repository.files.fields.FileExt]
                if file_ext is None:
                    file_ext = pathlib.Path(file[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
                doc_type = get_doc_type(file_ext)
                Repository.files.app(app.Name).context.update(
                    Repository.files.fields.id== file.id,
                    Repository.files.fields.DocType<<(doc_type[0].upper()+doc_type[1:])
                )
                if hasattr(config.process_services, doc_type):
                    try:
                        download_url, rel_path, download_file, token,share_id = local_api_service.get_download_path(file, app.Name)
                        if download_url is not None:

                            action_info = getattr(config.process_services, doc_type)
                            if action_info:
                                if action_key == "content":
                                    content = None
                                    if isinstance(action_info.get(action_key),dict)  and action_info.get(action_key).get('type')=="tika":
                                        if download_url is None:
                                            continue
                                        download_file =os.path.join("/socat-share",str(uuid.uuid4()))
                                        content = cy_utils.call_local_tika(
                                            action = action_info,
                                            action_type = action_key,
                                            url_file = download_url ,
                                            download_file = download_file
                                        )
                                    elif isinstance(action_info.get(action_key),dict)  and action_info.get(action_key).get('type')=="web-api":
                                        if download_url is None:
                                            continue
                                        content = cy_utils.call_web_api(
                                            data =action_info.get('content'),
                                            action_type=action_key,
                                            url_file=download_url,
                                            download_file=download_file,

                                        )

                                    if content is not None:
                                        content = cy_utils.texts.well_form_text(content)
                                        search_engine.update_content(
                                                app_name=app.Name,
                                                id=file.id,
                                                content=content,
                                                replace_content=True,
                                                data_item= file
                                            )

                                if action_key =="image":
                                    server_image_file_path = f"{rel_path}.png"
                                    if action_info.get(action_key) is None:
                                        continue
                                    if action_info.get(action_key).get('port')==1112:
                                        print("OK")


                                    client = Client(f"{process_services_host}:{action_info.get(action_key).get('port')}/")
                                    if download_url is None:
                                        continue
                                    _,result = client.predict(
                                        download_url,
                                        False,
                                        api_name="/predict"
                                    )
                                    image_file_path = f"{rel_path}.png"
                                    if os.path.isfile(result):
                                        local_api_service.send_file(
                                            file_path=result,
                                            token=token,
                                            local_share_id=share_id,
                                            app_name= app.Name,
                                            rel_server_path=image_file_path

                                        )
                                        if os.path.isfile(result):
                                            os.remove(result)


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
                        print(download_url)
                        print(ex)
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
