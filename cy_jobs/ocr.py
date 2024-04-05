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

local_api_service = cy_kit.singleton(LocalAPIService)
lv_ocr_service = cy_kit.singleton(LVOCRService)
msg = cy_kit.singleton(RabitmqMsg)
apps = Repository.apps.app("admin").context.find({})
finish = dict()
_apps = list(apps)
filter = Repository.files.fields.FileExt == "pdf"
filter = filter | (Repository.files.fields.MimeType.startswith("image/"))
filter = filter & (Repository.files.fields.IsLvOrc3 == None)

search_engine = cy_kit.singleton(SearchEngine)


def get_download_path(upload_item, app_name: str) -> typing.Tuple[str | None, str | None]:
    rel_file_path = None
    try:
        rel_file_path: str = upload_item["MainFileId"].split("://")[1]
    except:
        return None, None
    print(f"process file {rel_file_path} ...")
    local_share_id = None
    token = None
    server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
    # es_server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path+".search.es"
    if not upload_item.get("local_share_id"):
        token = local_api_service.get_access_token("admin/root", "root")
        server_file += f"?token={token}"
    else:
        local_share_id = upload_item["local_share_id"]
        server_file += f"?local-share-id={local_share_id}&app-name={app_name}"
    file_ext = pathlib.Path(rel_file_path).suffix
    download_file_path = os.path.join("/tmp-files", str(uuid.uuid4()) + file_ext)
    return server_file, download_file_path


for app in _apps:
    files_context = Repository.files.app(app.Name)
    files_context.context.update(
        {},
        Repository.files.fields.IsLvOrc3 << None
    )

while True:
    for app in _apps:
        # if finish.get(app.Name):
        #     continue
        files_context = Repository.files.app(app.Name)
        files = files_context.context.aggregate().match(
            filter
        ).sort(
            files_context.fields.RegisterOn.desc()
        ).limit(10)
        total = 0
        for item in files:
            server_file, download_file_path = get_download_path(item, app.Name)
            is_file_ok = False
            if server_file and download_file_path:
                try:
                    print(f"get file from {server_file}\n"
                          f"to {download_file_path} ...")
                    with open(server_file, "rb") as sf:
                        with open(download_file_path, "wb") as df:
                            df.write(sf.read())
                    print(f"get file from {server_file} \n"
                          f"to {download_file_path} is ok")
                    is_file_ok = True
                except:
                    print(f"get file from {server_file} \n"
                          f"to {download_file_path} was fail")

            if is_file_ok:
                text = None
                content = None
                try:
                    text = lv_ocr_service.do_orc(download_file_path)
                    content = texts.well_form_text(text)
                except Exception as ex:
                    txt_error = str(ex)
                    files_context.context.update(
                        files_context.fields.id == item.id,
                        files_context.fields.LvOcrErrorLogs << txt_error,
                        files_context.fields.IsLvOcrError << True
                    )
                    print(txt_error)
                try:
                    search_engine.update_content(
                        app_name=app.Name,
                        id=item.id,
                        content=content,
                        meta_data=None,
                        data_item=item,
                        replace_content=True
                    )
                except elasticsearch.exceptions.RequestError as ex:
                    txt_error = str(ex)
                    files_context.context.update(
                        files_context.fields.id == item.id,
                        files_context.fields.SearchEngineErrorLog << txt_error,
                        files_context.fields.IsSearchEngineError << True
                    )
                try:
                    os.remove(download_file_path)
                finally:
                    pass
            files_context.context.update(
                files_context.fields.id == item.id,
                files_context.fields.IsLvOrc3 << True
            )
            # if server_file is not None:
            # msg.emit(
            #     app_name=app.AppName,
            #     message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_IMAGE,
            #     require_tracking=True,
            #     data=item.to_json_convertable()
            #
            # )
            # files_context.context.update(
            #     files_context.fields.id == item.id,
            #     files_context.fields.IsLvOrc2 << True
            # )
            total += 1
        print(f"app={app.Name}, count={total}")
        if total == 0:
            finish[app.Name] = app.Name
print("Xong")
