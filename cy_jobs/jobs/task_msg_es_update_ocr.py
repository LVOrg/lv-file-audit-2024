#docker run -it --entrypoint=/bin/bash -v /mnt/files:/mnt/files docker.lacviet.vn/xdoc/lib-ocr-all:2
import os
import pathlib
import shutil
import sys
import traceback
import typing

from icecream import ic



sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
from cyx.common import config
if not hasattr(config,"msg_ocr"):
    raise Exception(f"msg_ocr was not found in config")
if not hasattr(config,"app_name"):
    raise Exception(f"app_name was not found in config")
msg_raise_ocr:str = config.msg_ocr
app_name =config.app_name
temp_ocr_file_dir_name="__temp_ocr_file__"
from cy_xdoc.services.search_engine import SearchEngine
import cy_kit
search_engine = cy_kit.single(SearchEngine)
from elasticsearch import Elasticsearch
from cyx.repository import Repository

import elasticsearch.exceptions
#/mnt/files/__temp_ocr_file__
class OCRContentInfo:
    app_name:str
    content_file:str
    upload_id:str

from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service =cy_kit.singleton(LogsToMongoDbService)
def scan_dir(folder:str)->typing.Iterable[OCRContentInfo]:
    for fx  in os.walk(folder):
        root_dir,_,files = fx
        app_name = pathlib.Path(root_dir).name
        for f in files:
            ret = OCRContentInfo()
            ret.app_name = app_name
            ret.upload_id =pathlib.Path(f).stem
            ret.content_file = os.path.join(root_dir,f)
            yield ret

def do_update_es(info:OCRContentInfo,client:Elasticsearch,app_name:str):


    content = None
    with open(info.content_file, "rb") as fs:
        content = fs.read().decode()
        ic(content[0:20])
    if isinstance(content, str) and len(content) > 0:
        update_body = {
            "doc": {
                "content": content
            }
        }
        index_name = search_engine.get_index(app_name)
        try:
            response = client.update(index=index_name, doc_type="_doc", id=info.upload_id, body=update_body)

            # Check the response
            if response.get('result') == 'updated':
                ic(f"Document updated successfully, info={info.__dict__}")
            else:
                data_item = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.id==info.upload_id
                )
                if data_item is None:
                    ic(f"File was delete {info.__dict__}")
                    return
                search_engine.make_index_content(
                    app_name = app_name,
                    upload_id= info.upload_id,
                    data_item=data_item.to_json_convertable(),
                    privileges= data_item[Repository.files.fields.Privileges],
                    content =content

                )
        except elasticsearch.exceptions.NotFoundError:
            data_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.id == info.upload_id
            )
            if data_item is None:
                ic(f"File was delete {info.__dict__}")
                return
            search_engine.make_index_content(
                app_name=app_name,
                upload_id=info.upload_id,
                data_item=data_item.to_json_convertable(),
                privileges=data_item[Repository.files.fields.Privileges],
                content=content

            )


def main():
    folder_path=os.path.join(config.file_storage_path,temp_ocr_file_dir_name,app_name)
    folder_path_processed = os.path.join(config.file_storage_path, temp_ocr_file_dir_name, f"__{app_name}__")
    os.makedirs(folder_path_processed,exist_ok=True)
    client: Elasticsearch = search_engine.client
    while True:
        for it in scan_dir(folder_path):
            try:
                info:OCRContentInfo =it
                ic(info.__dict__)
                do_update_es(info=info,client=client,app_name=app_name)
                move_to = os.path.join(folder_path_processed,f"{info.upload_id}.txt")

                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id==info.upload_id,
                    Repository.files.fields.HasORCContent<<True
                )
                shutil.move(info.content_file, move_to)
            except:
                logs_to_mongo_db_service.log(
                    error_content=traceback.format_exc(),
                    url=__name__
                )
                print(traceback.format_exc())






if __name__ == "__main__":
    main()
