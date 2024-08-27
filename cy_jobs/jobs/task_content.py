import datetime
import sys
import pathlib

import traceback

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
import gc
import time

import cy_kit
from cy_jobs.cy_job_libs import JobLibs
from cyx.repository import Repository

import cyx.common.msg
from cyx.rabbit_utils import Consumer, MesssageBlock


import cy_utils
from cyx.extract_content_service import ExtractContentService

import json
import pathlib

extract_content_service:ExtractContentService = cy_kit.singleton(ExtractContentService)


from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service:LogsToMongoDbService = cy_kit.singleton(LogsToMongoDbService)
def run():
    print("run")
    consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
    while True:
        time.sleep(1)
        try:
            gc.collect()

            msg = consumer.get_msg(delete_after_get=True)
            if isinstance(msg, MesssageBlock):
                file_item = {}
                app_name = msg.app_name
                upload_item = msg.data
                download_url:str = "unknown"
                try:

                    print(f"Process app={app_name}")

                    print(json.dumps(msg.data, indent=4))
                    download_url, rel_path, download_file, token, share_id = JobLibs.local_api_service.get_download_path(
                        upload_item, app_name
                    )
                    if download_url is None:
                        continue

                    file_item = Repository.files.app(msg.app_name).context.find_one(
                        Repository.files.fields.id == msg.data["_id"]
                    )
                    if not file_item:
                        continue
                    is_ready_content = (file_item.ProcessInfo or {}).get('content') and (
                            (file_item.ProcessInfo or {}).get('content', {}).get("IsError", "False") == "False")


                    file_ext = file_item[Repository.files.fields.FileExt]
                    if file_ext is None:
                        file_ext = pathlib.Path(file_item[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
                    doc_type = JobLibs.get_doc_type(file_ext)

                    if doc_type == "unknown":
                        continue
                    if doc_type == "pdf":
                        if not extract_content_service.health_check_ocr():
                            """
                            Service is really busy. So stop and move next msg
                            """
                            print(f"Ocr service at {extract_content_service.get_url()} was busy")
                            consumer.resume(msg)
                            continue
                        extract_content_service.update_by_using_ocr_pdf(
                            download_url=download_url,
                            data=file_item,
                            app_name=app_name
                        )
                        Repository.lv_file_content_process_report.app("admin").context.insert_one(
                            Repository.lv_file_content_process_report.fields.UploadId << upload_item.get("_id"),
                            Repository.lv_file_content_process_report.fields.LocalPath << download_url,
                            Repository.lv_file_content_process_report.fields.CustomerPath << upload_item.get(
                                "SyncFromPath") or "",
                            Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.now(datetime.UTC)
                        )
                    elif not is_ready_content:
                        if doc_type == "office":
                            extract_content_service.update_by_using_tika(
                                download_url=download_url,
                                rel_path=rel_path,
                                data=file_item,
                                app_name=app_name
                            )
                            Repository.lv_file_content_process_report.app("admin").context.insert_one(
                                Repository.lv_file_content_process_report.fields.UploadId << upload_item.get("_id"),
                                Repository.lv_file_content_process_report.fields.LocalPath << download_url,
                                Repository.lv_file_content_process_report.fields.CustomerPath << upload_item.get(
                                    "SyncFromPath") or "",
                                Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.now(datetime.UTC)
                            )

                        else:
                            continue


                except cy_utils.CallAPIException as ex:
                    JobLibs.process_manager_service.submit_error(
                        data=file_item,
                        app_name=app_name,
                        action_type="content",
                        error=str(ex)

                    )
                    Repository.lv_file_content_process_report.app("admin").context.insert_one(
                        Repository.lv_file_content_process_report.fields.UploadId << upload_item.get("_id"),
                        Repository.lv_file_content_process_report.fields.LocalPath << download_url,
                        Repository.lv_file_content_process_report.fields.CustomerPath << upload_item.get(
                            "SyncFromPath") or "",
                        Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.now(datetime.UTC),
                        Repository.lv_file_content_process_report.fields.IsError << True,
                        Repository.lv_file_content_process_report.fields.Error << traceback.format_exc()
                    )
                    logs_to_mongo_db_service.log(traceback.format_exc(),"task-content")

                except Exception as ex:
                    JobLibs.process_manager_service.submit_error(
                        data=file_item,
                        app_name=app_name,
                        action_type="content",
                        error=ex
                    )
                    Repository.lv_file_content_process_report.app("admin").context.insert_one(
                        Repository.lv_file_content_process_report.fields.UploadId << upload_item.get("_id"),
                        Repository.lv_file_content_process_report.fields.LocalPath << download_url,
                        Repository.lv_file_content_process_report.fields.CustomerPath << upload_item.get(
                            "SyncFromPath") or "",
                        Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.now(datetime.UTC),
                        Repository.lv_file_content_process_report.fields.IsError << True,
                        Repository.lv_file_content_process_report.fields.Error << traceback.format_exc()
                    )
                    logs_to_mongo_db_service.log(traceback.format_exc(), "task-content")
                    consumer.resume(msg)

                finally:
                    del upload_item
                    gc.collect()
            else:
                time.sleep(0.2)
                print("no message")
        finally:
            JobLibs.malloc_service.reduce_memory()



if __name__ == "__main__":
    print(__file__)
    try:
        run()
    except:
        logs_to_mongo_db_service.log(traceback.format_exc(), "task-content")
        print(traceback.format_exc())
