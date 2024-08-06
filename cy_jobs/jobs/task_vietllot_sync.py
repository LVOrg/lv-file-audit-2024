import sys
import pathlib
import traceback
import typing



sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/apps")
import datetime
import mimetypes
import os
import pathlib
import shutil
import time
import uuid

from cyx.common import config
from cyx.repository import Repository

default_tenant = config.default_tenant
file_dir_path = config.file_dir_path
print(default_tenant)
import humanize


def add_file(file_path, app_name, match_path):
    customer_dir = pathlib.Path(file_path).parent.__str__()

    upload_id = str(uuid.uuid4())
    file_name = pathlib.Path(file_path).name
    if file_name.startswith("'"):
        file_name = file_name[1:]
    if file_name.endswith("'"):
        file_name = file_name[:1]
    customer_file = os.path.join(customer_dir, file_name)
    file_name_only = pathlib.Path(file_path).stem
    for c in ["?", ":", "#", "/"]:
        file_name = file_name.replace(c, "_")
        file_name_only = file_name_only.replace(c, "_")
    file_ext = pathlib.Path(file_name).suffix
    register_on = datetime.datetime.utcnow()

    if file_ext:
        file_ext = file_ext[1:]
    file_ext_locate = file_ext[0:3] if file_ext else "unknown"
    main_file_id = os.path.join(app_name, register_on.strftime("%Y/%m/%d"), file_ext_locate, upload_id,
                                file_name.lower()).__str__()
    mime_type, _ = mimetypes.guess_type(file_path)
    local_file_path = os.path.join(config.file_storage_path, main_file_id).__str__()
    ret = Repository.files.app(app_name).context.insert_one(
        Repository.files.fields.id << upload_id,
        Repository.files.fields.FileName << file_name,
        Repository.files.fields.FileExt << file_ext,
        Repository.files.fields.FileNameLower << file_name.lower(),
        Repository.files.fields.MainFileId << f"local://{main_file_id}",
        Repository.files.fields.SyncFromPath << match_path,
        Repository.files.fields.MimeType << mime_type,
        Repository.files.fields.Status << 1,
        Repository.files.fields.FullFileName << f"{upload_id}/{file_name}",
        Repository.files.fields.FullFileNameLower << f"{upload_id}/{file_name}".lower(),
        Repository.files.fields.ServerFileName << f"{upload_id}.{file_ext}",
        Repository.files.fields.SizeInBytes << os.stat(file_path).st_size,
        Repository.files.fields.SizeInHumanReadable << humanize.naturalsize(os.stat(file_path).st_size),
        Repository.files.fields.RegisterOn << register_on,
        Repository.files.fields.StorageType << "local",
        Repository.files.fields.IsPublic << True,
        Repository.files.fields.IsPublic << True,
        Repository.files.fields.FullFileNameWithoutExtenstion << f"{upload_id}/{file_name_only}",
        Repository.files.fields.FullFileNameWithoutExtenstionLower << f"{upload_id}/{file_name_only}".lower(),
        Repository.files.fields.StoragePath << f"local://{main_file_id}"

    )
    os.makedirs(pathlib.Path(local_file_path).parent.__str__(), exist_ok=True)
    print(f"copy from {file_path}->{local_file_path}")
    shutil.copy(file_path, local_file_path)
    return upload_id,file_name.lower()

vietlott_data = "vietlott_Data"
from cy_docs import FUNCS
codx_dm_file_context = Repository.codx_dm_file_info.app(vietlott_data)
lv_file_sync_report_context = Repository.lv_file_sync_report.app(default_tenant)
test = codx_dm_file_remain = codx_dm_file_context.context.find_one({})
logs = Repository.lv_file_sync_logs.app("default")
logs.context.delete({})
# reset all data

lv_file_sync_report_context.context.delete({})

fx=Repository.files.fields.SyncFromPath!=None

import pymongo
if not test:
    raise Exception("Can not find DM_FileInfo in vietlott_Data")

# shutil.copy("/home/vmadmin/python/cy-py/cy_controllers/test(1).txt","/home/vmadmin/python/cy-py/cy_controllers/test_1_.txt")
# print(os.path.isfile("/home/vmadmin/python/cy-py/cy_controllers/test(1).txt"))
codx_dm_file_remain = codx_dm_file_context.context.aggregate().sort(
    codx_dm_file_context.fields.CreatedOn.desc()
).match(
    (((codx_dm_file_context.fields.UploadId == "")|(codx_dm_file_context.fields.UploadId == None)) &
     (codx_dm_file_context.fields.ImportFrom == "mysql"))
).limit(100)
codx_dm_file_remain = list(codx_dm_file_remain)
#/home/vmadmin/python/cy-py/cy_controllers/files/file_privileges_controller.py
# file_path_old_from_codx="modules/cy_controllers/files/file_privileges_controller.py"
# customer_file_path = os.path.join(file_dir_path, "/".join(file_path_old_from_codx.split('/')[1:])).__str__()
# upload_id, file_name_in_lv_file = add_file(customer_file_path, app_name="default", match_path=customer_file_path)
# customer_file_path = os.path.join(file_dir_path, "/".join(file_path_old_from_codx.split('/')[1:])).__str__()
while len(codx_dm_file_remain)>0:
    for dm_file in codx_dm_file_remain:
        # dm_file_id= dm_file.Id
        # if isinstance(dm_file.Id,str):
        #     dm_file_id= bson.ObjectId(dm_file_id)

        file_path_old_from_codx = dm_file[codx_dm_file_context.fields.FilePath_Old]
        if file_path_old_from_codx is None:
            continue
        file_dir_path="/mnt/customers"
        customer_file_path =os.path.join(file_dir_path, file_path_old_from_codx).__str__()
        print(f"Sync file {file_path_old_from_codx} \n"
              f"with mount {customer_file_path}")
        if not os.path.isfile(customer_file_path):
            lv_file_sync_report_context.context.insert_one(
                lv_file_sync_report_context.fields.FilePath<< file_path_old_from_codx,
                lv_file_sync_report_context.fields.SubmitOn << datetime.datetime.utcnow()
            )
            continue
        try:
            upload_item_with_path = Repository.files.app("default").context.find_one(
                Repository.files.fields.SyncFromPath==customer_file_path
            )
            if upload_item_with_path:
                codx_dm_file_context.context.update(
                    codx_dm_file_context.fields.id == dm_file.id,
                    codx_dm_file_context.fields.UploadId << upload_item_with_path.id,
                    codx_dm_file_context.fields.PathDisk << f"api/default/file/{upload_item_with_path.id}/{upload_item_with_path.FileName}"
                )
                logs.context.insert_one(
                    logs.fields.Error << f"Sync file from {file_path_old_from_codx} to {customer_file_path} is OK"
                )
            else:
                upload_id, file_name_in_lv_file = add_file(customer_file_path,app_name="default",match_path=customer_file_path)
                logs.context.insert_one(
                    logs.fields.Error <<f"Sync file from {file_path_old_from_codx} to {customer_file_path} is OK"
                )
                codx_dm_file_context.context.update(
                    codx_dm_file_context.fields.id==dm_file.id,
                    codx_dm_file_context.fields.UploadId <<  upload_id,
                    codx_dm_file_context.fields.PathDisk << f"api/default/file/{upload_id}/{file_name_in_lv_file}"
                )



        except:
            logs.context.insert_one(
                logs.fields.Error << traceback.format_exc().__str__()
            )
            print(traceback.format_exc())
            continue


