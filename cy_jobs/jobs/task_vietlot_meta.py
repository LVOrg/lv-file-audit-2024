import datetime
import os
import sys
import time
import traceback

sys.path.append("/app")
import cy_docs
from cyx.common.mongo_db_services import RepositoryContext
@cy_docs.define("update_meta_report")
class UpdateMetaReport:
    UploadId:str
    CodxId: str
    SubmitTime:datetime.datetime
    Error: str

report_res = RepositoryContext[UpdateMetaReport](UpdateMetaReport)


from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
search_engine=cy_kit.singleton(SearchEngine)
app_name = "default"
app_codx_name ="vietlott_Data"
from cyx.repository import Repository
# codx_mongodb="mongodb://admin:Erm%402021@172.16.7.33:27017"
from pymongo.mongo_client import MongoClient

# codx_client = MongoClient(codx_mongodb)
codx_files = Repository.codx_dm_file_info.app(app_codx_name)
# codx_files.__client__ = codx_client
n= datetime.datetime.now(datetime.UTC)
# data_test=codx_files.context.find_one({})
print((datetime.datetime.now(datetime.UTC) - n).total_seconds())
import elasticsearch.exceptions
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)
report_context=report_res.app(app_name)
from icecream import ic
def make_privileges(permissions):


    """
    "Privileges" : {
      "a" : [
        "1",
        "2",
        "3",
        "4"
      ],
      "b" : [
        "5",
        "6",
        "7",
        "8"
      ]
    }
    :param permissions:
    :return:
    """
    if not permissions:
        return {}

    es_privileges = [{(x.get("ObjectType") or "").lower(): [(x.get("ObjectID") or "").lower()]} for x in permissions]
    return es_privileges
total =1
mark_field = codx_files.fields.lv_file_services_is_update_meta_v1
count = 0
local_api_service = cy_kit.singleton(LocalAPIService)
import cyx.common.msg
consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
row_count =1
offset =0
from cyx.loggers import LoggerService

import cy_docs


def do_sync_meta(revrse:bool=False):

    update_time = "09"
    # ret = Repository.files.app(app_name).context.update(
    #     {},
    #     Repository.files.fields.UpdateMetaDataTime << update_time
    # )
    row_count = 1
    while row_count > 0:
        sort =  Repository.files.fields.RegisterOn.desc() if not revrse else  Repository.files.fields.RegisterOn.asc()
        lv_files = Repository.files.app(app_name).context.aggregate().match(
            (Repository.files.fields.UpdateMetaDataTime != update_time)|(Repository.files.fields.UpdateMetaDataTime == None)
        ).sort(
            sort
        ).project(
            cy_docs.fields.upload_id >> Repository.files.fields.id
        ).limit(100)
        ic(lv_files)

        total = 0
        items = list(lv_files)

        row_count = len(items)
        ic(f"reverse={revrse} fetch {row_count} items")
        for item in items:
            x = codx_files.context.aggregate().match(
                codx_files.fields.UploadId == item.upload_id
            ).project(
                cy_docs.fields.CodxId >> cy_docs.fields._id,
                codx_files.fields.FileName,
                codx_files.fields.FileSize,
                codx_files.fields.Permissions,
                codx_files.fields.UploadId,
                codx_files.fields.CreatedBy,
                codx_files.fields.CreatedOn,
                codx_files.fields.FolderPath,
                codx_files.fields.ObjectType,
                codx_files.fields.ObjectID

            ).first_item()
            if not x:
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.UpdateMetaDataTime << update_time,
                    # Repository.files.fields.SyncFromPath
                )
                continue
            try:
                check = [x for x in x[codx_files.fields.Permissions] if " " in (x.get("ObjectID") or "")]
                if len(check) > 0:
                    ic(x.CreatedOn)
                    ic(check)
                server_privileges = make_privileges(x[codx_files.fields.Permissions])
                local_api_service.generate_local_share_id(app_name=app_name, upload_id=x.UploadId)
                data_item = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.Id == item.upload_id
                )
                if not data_item:
                    total += 1

                    ic(f"Not found in doc {x.UploadId}")
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.Id == item.upload_id,
                        Repository.files.fields.UpdateMetaDataTime << update_time,
                        # Repository.files.fields.SyncFromPath
                    )
                    continue

                ic(f"Found in doc {x.UploadId}")
                meta_data = {
                    "FolderPath": x[codx_files.fields.FolderPath] or "",
                    "EntityName": x[codx_files.fields.ObjectType] or "",
                    "FileName": x[codx_files.fields.FileName] or "",
                    "CreatedBy": x[codx_files.fields.CreatedBy] or "",
                    "FileSize": x[codx_files.fields.FileSize] or 0,
                    "ObjectID": x[codx_files.fields.ObjectID] or "",
                    "ObjectType": x[codx_files.fields.ObjectType] or ""
                }
                if not {"1": [x.CreatedBy.lower()]} in server_privileges:
                    server_privileges += [{"1": [x.CreatedBy.lower()]}]
                if not {"7": [""]} in server_privileges:
                    server_privileges += [{"7": [""]}]
                client_privileges = {}
                """
                {"1":["2404230009"],"7":[""]}
                """
                for px in server_privileges:
                    for k, v in px.items():
                        if client_privileges.get(k) is None:
                            client_privileges[k] = []
                        client_privileges[k] += v
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.meta_data << meta_data,
                    Repository.files.fields.Privileges << client_privileges,
                    Repository.files.fields.ClientPrivileges << server_privileges,
                    Repository.files.fields.UpdateMetaDataTime << update_time,
                    # Repository.files.fields.SyncFromPath
                )
                data_item.meta_data = meta_data

                search_engine.create_or_update_privileges(
                    app_name=f"{app_name}",
                    upload_id=item.upload_id,
                    data_item=data_item,
                    privileges=server_privileges,
                    meta_info=meta_data,
                    force_replace=True

                )
                report_context.context.insert_one(
                    report_context.fields.UploadId << item.upload_id,
                    report_context.fields.CodxId << x.CodxId

                )
                ic(f"update meta {x.CodxId} with {item.upload_id} is OK")
                ic(meta_data)
            except elasticsearch.exceptions.NotFoundError as ex:

                logs_to_mongo_db_service.log(traceback.format_exc(), "task_vietlott_meta_update")
                ic(traceback.format_exc())
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << True,
                    # Repository.files.fields.SyncFromPath
                )
                report_context.context.insert_one(
                    report_context.fields.UploadId << item.upload_id,
                    report_context.fields.CodxId << x.CodxId,
                    report_context.fields.Error << traceback.format_exc()

                )
            except elasticsearch.exceptions.RequestError as ex:
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << True
                )
                report_context.context.insert_one(
                    report_context.fields.UploadId << item.upload_id,
                    report_context.fields.CodxId << x.CodxId,
                    report_context.fields.Error << traceback.format_exc()

                )
            except Exception as ex:

                ic(traceback.format_exc())
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.UpdateMetaDataTime << update_time
                )
                report_context.context.insert_one(
                    report_context.fields.UploadId << item.upload_id,
                    report_context.fields.CodxId << x.CodxId,
                    report_context.fields.Error << traceback.format_exc()

                )
            finally:
                total += 1
import multiprocessing

def run_parallel_processes():
    processes = []
    for reverse in [True, False]:
        process = multiprocessing.Process(target=do_sync_meta, args=(reverse,))
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join()
if __name__ == "__main__":
    run_parallel_processes()