import datetime
import sys
import time
import traceback

sys.path.append("/app")
from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
search_engine=cy_kit.singleton(SearchEngine)
app_name = "developer"
from cyx.repository import Repository
from pymongo.mongo_client import MongoClient
codx_mongodb="mongodb://admin:Erm%402021@172.16.7.33:27017/"
codx_client = MongoClient(codx_mongodb)
codx_files = Repository.codx_dm_file_info.app(f"{app_name}_Data")
codx_files.__client__ = codx_client
n= datetime.datetime.utcnow()
data_test=codx_files.context.find_one({})
print((datetime.datetime.utcnow()-n).total_seconds())
import elasticsearch.exceptions
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
mark_field = codx_files.fields.lv_file_services_is_update_meta_v5
count = 0
local_api_service = cy_kit.singleton(LocalAPIService)
import cyx.common.msg
consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
while total>0:
    items = codx_files.context.aggregate().match(
        ((mark_field == None) | (mark_field == False)) & (
            (codx_files.fields.UploadId!=None) & (codx_files.fields.UploadId!="")
        )
    ).sort(
        codx_files.fields.CreatedOn.desc()
    ).project(
        codx_files.fields.FileName,
        codx_files.fields.FileSize,
        codx_files.fields.Permissions,
        codx_files.fields.UploadId,
        codx_files.fields.CreatedBy,
        codx_files.fields.CreatedOn

    ).limit(100)
    total =0
    for x in items:
        try:
            check = [x for x in x[codx_files.fields.Permissions] if " " in (x.get("ObjectID") or "")]
            if len(check) > 0:
                print(x.CreatedOn)
                print(check)
            server_privileges = make_privileges(x[codx_files.fields.Permissions])
            local_api_service.generate_local_share_id(app_name=app_name, upload_id=x.UploadId)
            data_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.Id== x[codx_files.fields.UploadId]
            )
            if not data_item:
                total+=1
                print(f"Not found in Xdoc {x.UploadId}")
                if x.UploadId:
                    codx_files.context.update(
                        codx_files.fields.UploadId == x.UploadId,
                        mark_field << True
                    )
                continue


            meta_data = {
                "FolderPath":  x.FolderPath or "",
                "EntityName": x.ObjectType or "",
                "FileName" : x.FileName or "",
                "CreatedBy": x.CreatedBy or "",
                "FileSize": x.FileSize or 0,
                "ObjectID": x.ObjectID or "",
                "ObjectType": x.ObjecType or ""
            }
            if not {"1": x.CreatedBy.lower()} in server_privileges:
                server_privileges+=[{"1": x.CreatedBy.lower()}]
            if not {"7": [""]} in server_privileges:
                server_privileges+=[{"7": [""]}]
            Repository.files.app(app_name).context.update(
                Repository.files.fields.Id==x.UploadID,
                Repository.files.fields.meta_data << meta_data,
                Repository.files.fields.Privileges << server_privileges,
                Repository.files.fields.ClientPrivileges << server_privileges,
            )
            data_item.meta_data = meta_data



            search_engine.create_or_update_privileges(
                app_name=f"{app_name}",
                upload_id=x[codx_files.fields.UploadId],
                data_item= data_item,
                privileges=server_privileges,
                meta_info=meta_data

            )
            codx_files.context.update(
                codx_files.fields.UploadId==x.UploadId,
                mark_field<<True
            )


            consumer.raise_message(
                app_name=app_name,
                data=data_item.to_json_convertable()
            )
            print(x.UploadId)
        except elasticsearch.exceptions.NotFoundError as ex:
            raise ex
        except elasticsearch.exceptions.RequestError as ex:
            raise ex
        except Exception as ex:
            raise ex
        finally:
            total+=1
    count+=total
    print(f"total={count} items, wait net 10 seconds")
    time.sleep(10)