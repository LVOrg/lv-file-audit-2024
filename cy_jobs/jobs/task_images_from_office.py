import os
import sys
import pathlib

import traceback



sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
from cyx.common.brokers import Broker
import cyx.common.msg
import mimetypes
import cy_kit
from icecream import ic
from cyx.rabbit_utils import Consumer, MesssageBlock
import time
import gc
broker = cy_kit.singleton(Broker)
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongodb_service = cy_kit.singleton(LogsToMongoDbService)
from cyx.local_api_services import LocalAPIService
local_pai_service = cy_kit.singleton(LocalAPIService)
from cyx.file_utils_services import FileUtilService
file_util_service = cy_kit.singleton(FileUtilService)
from cyx.repository import Repository
from cyx.remote_caller import RemoteCallerService
remote_caller_service = cy_kit.singleton(RemoteCallerService)
from cyx.common import config
def run():
    consumer = Consumer(cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_OFFICE)
    while True:
        time.sleep(1)
        msg = None
        try:
            gc.collect()
            msg = consumer.get_msg(delete_after_get=False)
            if isinstance(msg, MesssageBlock):

                app_name = msg.app_name
                upload_item:dict|None = msg.data
                upload_id: str = upload_item.get("_id")
                upload_doc = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.id == upload_id
                )
                if not upload_doc:
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                ic(msg.data.get("_id"))
                ic(msg.data.get("real_file_location"))
                file_path = file_util_service.get_physical_path(
                    app_name = app_name,
                    upload_id = upload_id
                )
                ic(file_path)
                if not os.path.isfile(file_path):
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    ic(f"{file_path} was not found skip")
                    continue
                file_name = pathlib.Path(file_path).name
                url_resource ,_,_,_,_ = local_pai_service.get_download_path(
                    upload_item = upload_item,
                    app_name = app_name

                )
                url_upload_resource = local_pai_service.get_upload_path(
                    upload_item=upload_item,
                    app_name=app_name,
                    file_name = file_name,
                    file_ext="png"
                )
                ic(url_resource)
                ret = remote_caller_service.get_image_from_office(
                    url_of_office_to_image_service=config.remote_office,
                    url_of_content=url_resource,
                    url_upload_file =  url_upload_resource,
                    run_in_thread =False
                )
                if isinstance(ret,dict):
                    if ret.get("error"):
                        ic(ret.get("error"))
                        ic(ret.get("message"))
                        consumer.resume(msg)
                        continue

                ic(msg.data[Repository.files.fields.FullFileNameLower.__name__])
                broker.emit(
                    app_name = app_name,
                    message_type = cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                    data = msg.data
                )
                ic(cyx.common.msg.MSG_FILE_GENERATE_THUMBS)

        except:
            logs_to_mongodb_service.log(
                error_content=traceback.format_exc(),
                url=__file__
            )
            if msg:
                consumer.resume(msg)
        finally:
            gc.collect()
            consumer.channel.basic_ack(msg.method.delivery_tag)
if __name__ =="__main__":
    run()