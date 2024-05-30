import json
import pathlib
import sys
import traceback



sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append("/app")
import cy_kit
from cy_jobs.cy_job_libs import JobLibs
from  cyx.repository import Repository
print("start up")
import cyx.common.msg
from cyx.rabbit_utils import Consumer,MesssageBlock
consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
from cyx.common import config
import cy_utils
from cyx.extract_content_service import ExtractContentService
from cyx.common.rabitmq_message import RabitmqMsg
extract_content_service = cy_kit.singleton(ExtractContentService)
while True:
    msg = consumer.get_msg()
    if isinstance(msg,MesssageBlock):
        file_item ={}
        app_name = msg.app_name
        upload_item = msg.data
        try:

            print(f"Process app={app_name}")
            print(json.dumps(msg.data,indent=4))
            download_url, rel_path, download_file, token, share_id = JobLibs.local_api_service.get_download_path(
                upload_item, app_name
            )
            if download_url is None:
                continue
            file_context = Repository.files.app(msg.app_name).context
            file_item = Repository.files.app(msg.app_name).context.find_one(
                Repository.files.fields.id == msg.data["_id"]
            )
            if not file_item:
                continue
            is_ready_content = (file_item.ProcessInfo or {}).get('content') and (
                        (file_item.ProcessInfo or {}).get('content', {}).get("IsError", "False") == "False")

            is_ready_image = (file_item.ProcessInfo or {}).get('image') and (
                        (file_item.ProcessInfo or {}).get('image', {}).get("IsError", "False") == "False")
            file_ext = file_item[Repository.files.fields.FileExt]
            if file_ext is None:
                file_ext = pathlib.Path(file_item[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
            doc_type = JobLibs.get_doc_type(file_ext)

            if doc_type == "unknown":
                continue
            if not is_ready_content:
                extract_content_service.update_by_using_tika(
                download_url=download_url,
                rel_path=rel_path,
                data=file_item,
                app_name=app_name
            )


        except cy_utils.CallAPIException as ex:
            JobLibs.process_manager_service.submit_error(
                data= file_item,
                app_name=app_name,
                action_type="content",
                error=str(ex)

            )

        except Exception as ex:
            JobLibs.process_manager_service.submit_error(
                data=file_item,
                app_name=app_name,
                action_type="content",
                error=ex
            )
            consumer.resume(msg)
