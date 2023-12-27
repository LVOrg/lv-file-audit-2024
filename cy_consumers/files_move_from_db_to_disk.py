import datetime
import math
import os.path
import pathlib
import sys
from typing import TypeVar

import bson
import cy_kit
import pymongo.database
import gridfs.errors
from tqdm import tqdm
T = TypeVar('T')
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_docs
from cyx.common import config
from cyx.common.mongo_db_services import MongodbService

mongodb_service = cy_kit.single(MongodbService)
from cy_xdoc.models.files import DocUploadRegister
from cy_xdoc.models.apps import App
from cyx.cache_service.memcache_service import MemcacheServices
cache = cy_kit.singleton(MemcacheServices)
file_storage_path = config.file_storage_path
if not os.path.isdir(file_storage_path):
    raise Exception(f"{file_storage_path} was not found")


def get_app_dir(app_name: str) -> str:
    ret = os.path.join(file_storage_path, app_name)
    os.makedirs(ret, exist_ok=True)
    return ret


from gridfs import GridFS


def do_download_file(db: pymongo.database.Database, fs_id: bson.ObjectId, file_name: str, to_folder: str):
    try:
        fs = GridFS(db)
        grid_out = fs.get(fs_id)
        full_file_path = os.path.join(
            to_folder,
            file_name
        )
        chunk_size = (1024 ** 2) * 5
        file_size = grid_out.length
        range_length = int(math.floor(file_size / chunk_size))
        if file_size % chunk_size > 0:
            range_length += 2

        if os.path.isfile(full_file_path):
            os.remove(full_file_path)
        for i in tqdm(range(range_length)):
            data = grid_out.read(chunk_size)
            if len(data) > 0:
                if not os.path.isfile(full_file_path):
                    with open(full_file_path, "wb") as f:  # Replace with desired output filename
                        f.write(data)
                else:
                    with open(full_file_path, "ab") as f:  # Replace with desired output filename
                        f.write(data)

    except gridfs.errors.CorruptGridFile:
        pass
    # fs.delete(fs_id)


def do_download_thumbs(db: pymongo.database.Database, available_thumbs, to_folder, file_name):
    fs = GridFS(db)
    file_name_only = pathlib.Path(file_name).stem.replace(".", "_")
    for x in available_thumbs:
        try:
            fs_thumbs = fs.find_one({
                "rel_file_path": x
            })
            if fs_thumbs:
                download_file_path = os.path.join(
                    to_folder,
                    f"{file_name_only}_{x.split('/')[-1]}"

                )
                with open(download_file_path, "wb") as f:  # Replace with desired output filename
                    f.write(fs_thumbs.read())
                # fs.delete(fs_thumbs._id)
            else:
                print(f"{x} was not found in mongodb")
        except gridfs.errors.CorruptGridFile:
            pass


def move_data(app_name: str):
    ret_count = 0
    file_context = mongodb_service.db(app_name).get_document_context(DocUploadRegister)
    agg = file_context.context.aggregate().sort(
        file_context.fields.RegisterOn.desc()
    ).match(
        cy_docs.not_exists(file_context.fields.StoragePath) & (file_context.fields.Status == 1)

    ).limit(10)
    for x in agg:
        try:

            main_file_id = x[file_context.fields.MainFileId]
            main_thumb_id = x[file_context.fields.ThumbFileId]
            register_on: datetime.datetime = x[file_context.fields.RegisterOn]
            file_name = x[file_context.fields.FullFileNameLower]
            if not file_name:
                file_name = x[file_context.fields.FullFileName]
            file_name = file_name.lower().split('/')[1]
            file_ext = x[file_context.fields.FileExt]
            upload_id = x.id
            print(f"move file {file_name}.{file_ext}, size = {x[file_context.fields.SizeInBytes]}")
            if file_ext is None:
                file_ext = "unknown"
            else:
                file_ext = file_ext[0:3].lower()
            str_year = f"{register_on.year:04d}"
            str_month = f"{register_on.month:02d}"
            str_day = f"{register_on.day:02d}"
            rel_path = os.path.join(
                app_name,
                str_year,
                str_month,
                str_day,
                file_ext,
                upload_id
            )
            full_path = os.path.join(
                file_storage_path,
                rel_path
            )
            if not os.path.isdir(full_path):
                os.makedirs(full_path, exist_ok=True)
            fs_id = main_file_id
            if isinstance(fs_id, str):
                try:
                    fs_id = bson.ObjectId(fs_id)
                except bson.errors.InvalidId:
                    continue
            do_download_file(
                db=file_context.__client__.get_database(file_context.__db_name__),
                fs_id=fs_id,
                file_name=file_name,
                to_folder=full_path
            )
            if main_thumb_id:
                if isinstance(main_thumb_id, str):
                    try:
                        main_thumb_id = bson.ObjectId(main_thumb_id)
                    except bson.errors.InvalidId:
                        continue
                print(main_thumb_id)
                do_download_file(
                    db=file_context.__client__.get_database(file_context.__db_name__),
                    fs_id=main_thumb_id,
                    file_name=f"{file_name}.webp",
                    to_folder=full_path
                )
            available_thumbs = x[file_context.fields.AvailableThumbs]
            if isinstance(available_thumbs, list):
                do_download_thumbs(db=file_context.__client__.get_database(file_context.__db_name__),
                                   available_thumbs=available_thumbs, to_folder=full_path, file_name=file_name)



        except gridfs.errors.NoFile:
            pass
        file_context.context.update(
            file_context.fields.id == upload_id,
            file_context.fields.StorageType << 'local',
            file_context.fields.StoragePath << f"local://{rel_path}/{file_name}",
            file_context.fields.MainFileId << f"local://{rel_path}/{file_name}"
        )
        cache.clear_all()
        ret_count += 1
        # return ret_count
    return ret_count


def do_move_all(app_name: str):
    move_count = move_data(app_name)
    while move_count > 0:
        move_count = move_data(app_name)
    print("Xong roi")


# app_name="lv-test"
# do_move_all(app_name)

db_names = mongodb_service.db("admin").client.list_database_names()
app_qr = mongodb_service.db("admin").get_document_context(App)
apps = mongodb_service.db("admin").get_document_context(App).context.find(
    app_qr.fields.NameLower!="default"
)
for x in apps:
    do_move_all(x[app_qr.fields.NameLower])

