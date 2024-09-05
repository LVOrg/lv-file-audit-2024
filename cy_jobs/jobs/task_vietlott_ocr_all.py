
import datetime
import pathlib
import os
import sys

from retry import retry

sys.path.append("/app")
from icecream import ic
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
import time
import traceback

from cy_jobs.web import health_check

from retry import retry

from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
search_engine=cy_kit.singleton(SearchEngine)
app_name = "default"
app_name = "developer"
from cyx.repository import Repository
# codx_mongodb="mongodb://admin:Erm%402021@172.16.7.33:27017"
from pymongo.mongo_client import MongoClient
# codx_mongodb=co
n= datetime.datetime.now(datetime.UTC)
# data_test=codx_files.context.find_one({})
# print((datetime.datetime.now(datetime.UTC)-n).total_seconds())
import elasticsearch.exceptions
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)

total =1

count = 0
local_api_service = cy_kit.singleton(LocalAPIService)
import cyx.common.msg
consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
row_count =1
offset =0
from cyx.loggers import LoggerService
from cy_jobs.cy_job_libs import JobLibs
import cy_docs


from cyx.extract_content_service import ExtractContentService
from cyx.common.rabitmq_message import RabitmqMsg
import json
import pathlib
logs_to_mongo_db_service.log(traceback.format_exc(), "task_vietlott_meta_update")
extract_content_service = cy_kit.singleton(ExtractContentService)
def run(sort_rev=True):
    sort_expr = Repository.files.fields.RegisterOn.desc() if sort_rev else Repository.files.fields.RegisterOn.asc()
    row_count =1
    while row_count>0:
        lv_files = Repository.files.app(app_name).context.aggregate().match(
            Repository.files.fields.FileExt == "pdf"
        ).match(
            Repository.files.fields.Status == 1
        ).match(
            ((Repository.files.fields.IsHasORCContent==False)|
             (Repository.files.fields.IsHasORCContent=="false")|
             (Repository.files.fields.IsHasORCContent==None)
            )
        ).sort(
            sort_expr
        ).project(
            cy_docs.fields.upload_id>> Repository.files.fields.id,
            cy_docs.fields.download_url >> Repository.files.fields.FullFileNameLower
        ).limit(100)
        total =0
        items = list(lv_files)
        row_count = len(items)
        ic(f"fetch {row_count} items")
        @retry(ZeroDivisionError, tries=10, delay=5)
        def get_es_source(app:str,id:str):
            es_doc_item = search_engine.get_doc(
                app_name=app_name,
                id=item.upload_id
            )
            return es_doc_item
        for item in items:
            ic(item.upload_id)
            es_doc_item = get_es_source(app=app_name,id=item.upload_id)
            check = (es_doc_item and hasattr(es_doc_item,"source") and
                     hasattr(es_doc_item.source,"content") and
                     isinstance(es_doc_item.source.content,str) and
                     len(es_doc_item.source.content)>0)
            if check:
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id==item.upload_id,
                    Repository.files.fields.IsHasORCContent<< True
                )
                continue
            download_url = ""
            try:

                local_api_service.generate_local_share_id(app_name=app_name, upload_id=item.upload_id)
                data_item = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.Id== item.upload_id
                )
                ic(data_item.FullFileName)
                if not data_item:
                    total+=1
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.Id == item.upload_id,
                        Repository.files.fields.IsHasORCContent << True,
                        # Repository.files.fields.SyncFromPath
                    )
                    continue

                download_url, rel_path, download_file, token, share_id = JobLibs.local_api_service.get_download_path(
                    data_item.to_json_convertable(), app_name
                )

                import pathlib
                file_ext = data_item[Repository.files.fields.FileExt]
                if file_ext is None:
                    file_ext = pathlib.Path(data_item[Repository.files.fields.FileNameLower]).suffix.replace(".", "")
                doc_type = JobLibs.get_doc_type(file_ext)
                if doc_type == "pdf":
                    health_check_ocr = extract_content_service.health_check_ocr(5)
                    while not health_check_ocr:
                        ic(f'{extract_content_service.get_url()} is really busy')
                        health_check_ocr = extract_content_service.health_check_ocr(5)
                    extract_content_service.update_by_using_ocr_pdf(
                        download_url=download_url,

                        data=data_item,
                        app_name=app_name
                    )
                    Repository.lv_file_content_process_report.app("admin").context.insert_one(
                        Repository.lv_file_content_process_report.fields.UploadId << data_item.get("_id"),
                        Repository.lv_file_content_process_report.fields.LocalPath << download_url,
                        Repository.lv_file_content_process_report.fields.CustomerPath << data_item.get(
                            "SyncFromPath") or "",
                        Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.now(datetime.UTC)
                    )
                    ic(f'ocr {data_item.get("_id")} is ok')
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.Id == item.upload_id,
                        Repository.files.fields.IsHasORCContent << True,
                        # Repository.files.fields.SyncFromPath
                    )
                else:
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.Id == item.upload_id,
                        Repository.files.fields.IsHasORCContent << True,
                        # Repository.files.fields.SyncFromPath
                    )
            except elasticsearch.exceptions.NotFoundError as ex:

                logs_to_mongo_db_service.log(traceback.format_exc(),download_url)
                print(traceback.format_exc())
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << False,
                    # Repository.files.fields.SyncFromPath
                )
            except elasticsearch.exceptions.RequestError as ex:

                logs_to_mongo_db_service.log(traceback.format_exc(), download_url)
                print(traceback.format_exc())
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << False,
                    # Repository.files.fields.SyncFromPath
                )
            except Exception as ex:

                logs_to_mongo_db_service.log(traceback.format_exc(), download_url)
                print(traceback.format_exc())
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << False,
                    Repository.files.fields.IsHasORCContent << True
                    # Repository.files.fields.SyncFromPath
                )
            finally:
                total+=1
        time.sleep(1)
import multiprocessing
def run_parallel_processes():
    processes = []
    for reverse in [True, False]:
        process = multiprocessing.Process(target=run, args=(reverse,))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
if __name__ == "__main__":
    # run(sort_rev=False)
    run_parallel_processes()

