import sys
import pathlib
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

def add_file(file_path, app_name):
    upload_id = str(uuid.uuid4())
    file_name = pathlib.Path(file_path).name
    file_name_only = pathlib.Path(file_path).stem
    for c in ["?",":","#","/"]:
        file_name=file_name.replace(c,")")
        file_name_only=file_name_only.replace(c,")")
    file_ext = pathlib.Path(file_path).suffix
    register_on = datetime.datetime.utcnow()

    if file_ext:
        file_ext= file_ext[1:]
    file_ext_locate = file_ext[0:3] if file_ext else "unknown"
    main_file_id= os.path.join(app_name,register_on.strftime("%Y/%m/%d"),file_ext_locate,upload_id,file_name.lower())
    mime_type, _ = mimetypes.guess_type(file_path)
    local_file_path = os.path.join(config.file_storage_path, main_file_id)
    ret =Repository.files.app(app_name).context.insert_one(
        Repository.files.fields.id<<upload_id,
        Repository.files.fields.FileName <<file_name,
        Repository.files.fields.FileExt <<file_ext,
        Repository.files.fields.FileNameLower<<file_name.lower(),
        Repository.files.fields.MainFileId<<f"local://{main_file_id}",
        Repository.files.fields.SyncFromPath << file_path,
        Repository.files.fields.MimeType << mime_type,
        Repository.files.fields.Status<< 1,
        Repository.files.fields.FullFileName << f"{upload_id}/{file_name}",
        Repository.files.fields.FullFileNameLower<< f"{upload_id}/{file_name}".lower(),
        Repository.files.fields.ServerFileName << f"{upload_id}.{file_ext}",
        Repository.files.fields.SizeInBytes << os.stat(file_path).st_size,
        Repository.files.fields.SizeInHumanReadable << humanize.naturalsize(os.stat(file_path).st_size),
        Repository.files.fields.RegisterOn << register_on,
        Repository.files.fields.StorageType<<"local",
        Repository.files.fields.IsPublic << True,
        Repository.files.fields.FullFileNameWithoutExtenstion<<f"{upload_id}/{file_name_only}",
        Repository.files.fields.FullFileNameWithoutExtenstionLower << f"{upload_id}/{file_name_only}".lower(),
        Repository.files.fields.StoragePath<<f"local://{main_file_id}"



    )
    os.makedirs(pathlib.Path(local_file_path).parent.__str__(),exist_ok=True)
    shutil.copy(file_path,local_file_path)
    print("OK")
    # pass


def sync_all_file(folder,app_name):

    for x in os.walk(folder):
        root, dirs, files = x
        for file in files:
            full_file_path = os.path.join(root,file)
            upload = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.SyncFromPath==full_file_path
            )
            if not upload:
                add_file(file_path=full_file_path,app_name=app_name)
            time.sleep(0.5)
            sub_folders = [os.path.join(root,folder) for folder in dirs]
            for sub_dir in sub_folders:
                sync_all_file(sub_dir,app_name)
                time.sleep(0.5)
            print(file)

sync_all_file(file_dir_path,default_tenant)
