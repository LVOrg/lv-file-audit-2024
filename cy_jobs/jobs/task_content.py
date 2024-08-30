import datetime
import mimetypes
import os
import sys
import pathlib

import traceback


sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")
from icecream import ic

from cyx.common import config
import gc
import time

import cy_kit
from cy_jobs.cy_job_libs import JobLibs
from cyx.repository import Repository

import cyx.common.msg
from cyx.rabbit_utils import Consumer, MesssageBlock

import cy_utils
from cyx.extract_content_service import ExtractContentService

import json
import pathlib
from cyx.file_utils_services import FileUtilService
import re
extract_content_service: ExtractContentService = cy_kit.singleton(ExtractContentService)

file_util_service = cy_kit.singleton(FileUtilService)
from cyx.logs_to_mongo_db_services import LogsToMongoDbService

logs_to_mongo_db_service: LogsToMongoDbService = cy_kit.singleton(LogsToMongoDbService)
from cyx.common.brokers import Broker
import cyx.common.msg
import mimetypes
from cyx.common.rabitmq_message import RabitmqMsg
broker = cy_kit.singleton(RabitmqMsg)

def run():
    print("run")
    consumer = Consumer(cyx.common.msg.MSG_FILE_GENERATE_CONTENT)
    while True:
        time.sleep(1)
        try:
            gc.collect()

            msg = consumer.get_msg(delete_after_get=False)
            if isinstance(msg, MesssageBlock):

                app_name = msg.app_name
                upload_item: dict[str, any] = msg.data
                upload_id: str = upload_item.get("_id")
                upload_doc = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.id == upload_id
                )
                if not upload_doc:
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                file_path = file_util_service.get_physical_path(app_name=app_name, upload_id=upload_id)
                if not os.path.isfile(file_path):
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                file_suffix = pathlib.Path(file_path).suffix
                file_ext = file_suffix[1:]
                pattern = r"\.\w+-version-\d+"
                if re.match(pattern,file_suffix):
                   file_ext = file_suffix.split('-')[0][1:]
                m_t,_ = mimetypes.guess_type(f"a.{file_ext}")
                ic(f"receive msg ")
                ic(msg.data.get("_id"))
                ic(msg.data.get("real_file_location"))
                if file_ext.lower()=="pdf":
                    broker.emit(
                        app_name = app_name,
                        message_type=cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_PDF,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_PDF)
                    broker.emit(
                        app_name=app_name,
                        message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_PDF,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_PDF)
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                if file_ext.lower() in config.ext_office_file:
                    broker.emit(
                        app_name = app_name,
                        message_type=cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_OFFICE,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_OFFICE)
                    broker.emit(
                        app_name=app_name,
                        message_type= cyx.common.msg.MSG_EXTRACT_TEXT_FROM_OFFICE_FILE,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_EXTRACT_TEXT_FROM_OFFICE_FILE)
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                if m_t.startswith("image/"):
                    broker.emit(
                        app_name=app_name,
                        message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_GENERATE_THUMBS)
                    broker.emit(
                        app_name=app_name,
                        message_type=cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_OFFICE,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_OFFICE)
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
                if m_t.startswith("video/"):
                    broker.emit(
                        app_name=app_name,
                        message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO,
                        data=msg.data
                    )
                    ic(cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO)
                    consumer.channel.basic_ack(delivery_tag=msg.method.delivery_tag)
                    continue
        except:
            print(traceback.format_exc())




if __name__ == "__main__":
    print(__file__)
    try:
        run()
    except:
        logs_to_mongo_db_service.log(traceback.format_exc(), "task-content")
        print(traceback.format_exc())
