
import datetime
import pathlib
import os
import sys
sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
import time
import traceback

from cy_jobs.web import health_check



from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
search_engine=cy_kit.singleton(SearchEngine)
app_name = "default"
#app_name = "developer"
from cyx.repository import Repository
# codx_mongodb="mongodb://admin:Erm%402021@172.16.7.33:27017"
from pymongo.mongo_client import MongoClient
# codx_mongodb=co
n= datetime.datetime.now(datetime.UTC)
# data_test=codx_files.context.find_one({})
print((datetime.datetime.now(datetime.UTC)-n).total_seconds())
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
while row_count>0:
    lv_files = Repository.files.app(app_name).context.aggregate().match(
        ((Repository.files.fields.IsHasORCContent==False)|
         (Repository.files.fields.IsHasORCContent=="false")|
         (Repository.files.fields.IsHasORCContent==None)
        )&(Repository.files.fields.Status==1)
    ).sort(
        Repository.files.fields.RegisterOn.desc()
    ).project(
        cy_docs.fields.upload_id>> Repository.files.fields.id,
        cy_docs.fields.download_url >> Repository.files.fields.FullFileNameLower
    ).limit(100)
    total =0
    items = list(lv_files)
    row_count = len(items)
    print(f"fetch {row_count} items")
    for item in items:
        print(item.upload_id)
        es_doc_item = search_engine.get_doc(
            app_name=app_name,
            id=item.upload_id
        )
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

        try:

            local_api_service.generate_local_share_id(app_name=app_name, upload_id=item.upload_id)
            data_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.Id== item.upload_id
            )
            print(data_item.FullFileName)
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
                    print(f'{extract_content_service.get_url()} is really busy')
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
                print(f'ocr {data_item.get("_id")} is ok')
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

            logs_to_mongo_db_service.log(traceback.format_exc(),"task_vietlott_meta_update")
            print(traceback.format_exc())
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
        except elasticsearch.exceptions.RequestError as ex:

            logs_to_mongo_db_service.log(traceback.format_exc(), "task_vietlott_meta_update")
            print(traceback.format_exc())
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
        except Exception as ex:

            logs_to_mongo_db_service.log(traceback.format_exc(), "task_vietlott_meta_update")
            print(traceback.format_exc())
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
        finally:
            total+=1
    count+=total
    print(f"total={count} items, wait net 10 seconds")
    time.sleep(10)
    offset+=row_count



