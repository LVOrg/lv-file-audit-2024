import os.path
import sys
import pathlib

import bson.objectid

sys.path.append("/app")
from gridfs import GridFS
from cyx.common import config
file_storage_path= config.file_storage_path
import cy_docs
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
from cyx.repository import Repository
qtsc_default = Repository.apps.app("admin").context.find_one(
    Repository.apps.fields.Name=="default"
)
apps = Repository.apps.app("admin").context.aggregate().project(
    Repository.apps.fields.Name
)
apps = list(apps)
for app in apps:
    db = Repository.files.app(app.Name).context.collection.database
    fs = GridFS(db)
    files = Repository.files.app(app.Name).context.aggregate().match(
        { "MainFileId": { "$type": "objectId" } }).project(
        Repository.files.fields.Id,
        Repository.files.fields.MainFileId,
        Repository.files.fields.RegisterOn,
        Repository.files.fields.FileExt,
        Repository.files.fields.FileName,
        Repository.files.fields.ServerFileName,
        Repository.files.fields.StoragePath,
        Repository.files.fields.FullFileName
    )
    for x in files:
        file_id = None
        try:
            file_id = bson.objectid.ObjectId(x.MainFileId)
        except:
            continue
        if fs.find_one({"_id":file_id}):
            file_object = fs.get(file_id)
            RegisterOn= x.RegisterOn
            formatted_date = RegisterOn.strftime("%Y/%m/%d")
            file_ext_folder= "unknown"
            if x.FileExt:
                file_ext_folder = x.FileExt[0:3]
            file_name_lower = x.FileName.lower()
            url=f"{app.Name}/{x.FullFileName}"
            url2=f"http://172.16.7.99/lvfile/api/{app.Name}/file/{x.FullFileName}"
            print(url2)
            local_file_path = os.path.join(file_storage_path,app.Name,formatted_date,file_ext_folder)
            #default/48d0ef1f-b25e-46ff-b321-da38da1b7173/png-clipart-c-programming-language-logo-microsoft-visual-studio-net-framework-javascript-icon-purple-logo.png
            print(local_file_path)


