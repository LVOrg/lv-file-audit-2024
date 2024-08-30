import datetime
import os
import sys
import time
import traceback

sys.path.append("/app")

from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
search_engine=cy_kit.singleton(SearchEngine)
app_name = "default"
from cyx.repository import Repository
# codx_mongodb="mongodb://admin:Erm%402021@172.16.7.33:27017"
# from pymongo.mongo_client import MongoClient
# codx_mongodb=co
# codx_client = MongoClient(codx_mongodb)
codx_files = Repository.codx_dm_file_info.app(f"vietlott_Data")
# codx_files.__client__ = codx_client
n= datetime.datetime.utcnow()
# data_test=codx_files.context.find_one({})
print((datetime.datetime.utcnow()-n).total_seconds())
import elasticsearch.exceptions
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)
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
def clear_console():
    print('\033[2J\033[H', end='')

ret = Repository.files.app(app_name).context.update(
    {},
    Repository.files.fields.UpdateMetaDataTime << "2"
)

while row_count>0:
    lv_files = Repository.files.app(app_name).context.aggregate().sort(
        Repository.files.fields.RegisterOn.desc()
    ).project(
        cy_docs.fields.upload_id>> Repository.files.fields.id
    ).limit(100)

    clear_console()

    total =0
    items = list(lv_files)
    row_count = len(items)
    print(f"fetch {row_count} items")
    for item in items:
        x = codx_files.context.aggregate().match(
            codx_files.fields.UploadId == item.upload_id
        ).project(
            codx_files.fields.FileName,
            codx_files.fields.FileSize,
            codx_files.fields.Permissions,
            codx_files.fields.UploadId,
            codx_files.fields.CreatedBy,
            codx_files.fields.CreatedOn,
            codx_files.fields.FolderPath,
            codx_files.fields.ObjectType

        ).first_item()
        if not x:
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
            continue
        try:
            check = [x for x in x[codx_files.fields.Permissions] if " " in (x.get("ObjectID") or "")]
            if len(check) > 0:
                print(x.CreatedOn)
                print(check)
            server_privileges = make_privileges(x[codx_files.fields.Permissions])
            local_api_service.generate_local_share_id(app_name=app_name, upload_id=x.UploadId)
            data_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.Id== item.upload_id
            )
            if not data_item:
                total+=1
                clear_console()
                print(f"Not found in doc {x.UploadId}")
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.Id == item.upload_id,
                    Repository.files.fields.IsUpdateSearchFromCodx << True,
                    # Repository.files.fields.SyncFromPath
                )
                continue
            clear_console()
            print(f"Found in doc {x.UploadId}")
            meta_data = {
                "FolderPath":  x[codx_files.fields.FolderPath] or "",
                "EntityName": x[codx_files.fields.ObjectType] or "",
                "FileName" : x[codx_files.fields.FileName] or "",
                "CreatedBy": x[codx_files.fields.CreatedBy] or "",
                "FileSize": x[codx_files.fields.FileSize] or 0,
                "ObjectID": x[codx_files.fields.ObjectID] or "",
                "ObjectType": x[codx_files.fields.ObjectType] or ""
            }
            if not {"1": [x.CreatedBy.lower()]} in server_privileges:
                server_privileges+=[{"1": [x.CreatedBy.lower()]}]
            if not {"7": [""]} in server_privileges:
                server_privileges+=[{"7": [""]}]
            client_privileges={}
            """
            {"1":["2404230009"],"7":[""]}
            """
            for px  in server_privileges:
                for k,v in px.items():
                    if client_privileges.get(k) is None:
                        client_privileges[k]=[]
                    client_privileges[k]+=v
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id==item.upload_id,
                Repository.files.fields.meta_data << meta_data,
                Repository.files.fields.Privileges << client_privileges,
                Repository.files.fields.ClientPrivileges << server_privileges,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
            data_item.meta_data = meta_data



            search_engine.create_or_update_privileges(
                app_name=f"{app_name}",
                upload_id=item.upload_id,
                data_item= data_item,
                privileges=server_privileges,
                meta_info=meta_data,
                force_replace=True

            )
            # codx_files.context.update(
            #     codx_files.fields.UploadId==x.UploadId,
            #     mark_field<<True
            # )


            # consumer.raise_message(
            #     app_name=app_name,
            #     data=data_item.to_json_convertable()
            # )
            # Repository.lv_file_content_process_report.app("admin").context.find_one(
            #     Repository.lv_file_content_process_report.fields.Error << f"Update ok {x.UploadId}",
            #     Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.utcnow()
            # )
        except elasticsearch.exceptions.NotFoundError as ex:
            # Repository.lv_file_content_process_report.app("admin").context.find_one(
            #     Repository.lv_file_content_process_report.fields.Error << traceback.format_exc(),
            #     Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.utcnow()
            # )
            logs_to_mongo_db_service.log(traceback.format_exc(),"task_vietlott_meta_update")
            print(traceback.format_exc())
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
        except elasticsearch.exceptions.RequestError as ex:
            # Repository.lv_file_content_process_report.app("admin").context.find_one(
            #     Repository.lv_file_content_process_report.fields.Error << traceback.format_exc(),
            #     Repository.lv_file_content_process_report.fields.SubmitOn <<datetime.datetime.utcnow()
            # )
            logs_to_mongo_db_service.log(traceback.format_exc(), "task_vietlott_meta_update")
            print(traceback.format_exc())
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id == item.upload_id,
                Repository.files.fields.IsUpdateSearchFromCodx << True,
                # Repository.files.fields.SyncFromPath
            )
        except Exception as ex:
            # Repository.lv_file_content_process_report.app("admin").context.find_one(
            #     Repository.lv_file_content_process_report.fields.Error << traceback.format_exc(),
            #     Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.utcnow()
            # )
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