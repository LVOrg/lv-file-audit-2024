import pathlib
import sys
import time
import traceback

from icecream import ic

from cyx.repository import Repository

sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.rabbit_utils import Consumer
import cyx.common.msg
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
from cyx.local_api_services import LocalAPIService
from cyx.extract_content_service import ExtractContentService
extract_content_service = cy_kit.singleton(ExtractContentService)
logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)
local_file_service = cy_kit.singleton(LocalAPIService)
from cyx.common import config
import time
def run():
    ic("run")
    consumer = Consumer(cyx.common.msg.MSG_FILE_OCR_CONTENT_FROM_PDF)
    while True:
        msg = consumer.get_msg(delete_after_get=False)
        if msg is None:
            continue
        try:

            data = msg.data
            if not data:
                continue
            ic(data)
            upload_id = data.get("_id")

            app_name = msg.app_name

            ic(f"receive {upload_id}")
            upload_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.id == upload_id
            )
            if not upload_item:
                consumer.channel.basic_ack(msg.method.delivery_tag)
                continue
            download_url,_,_,_,_ = local_file_service.get_download_path(
                upload_item = data,
                app_name = app_name
            )
            url_of_ocr = config.remote_ocr
            health_check_ocr = extract_content_service.health_check_ocr(5)
            while not health_check_ocr:
                ic(f'{extract_content_service.get_url()} is really busy')
                health_check_ocr = extract_content_service.health_check_ocr(5)

            extract_content_service.update_by_using_ocr_pdf(
                download_url=download_url,

                data=upload_item,
                app_name=app_name
            )
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id==upload_id,
                Repository.files.fields.HasORCContent << True
            )
        except:
            logs_to_mongo_db_service.log(
                error_content =traceback.format_exc(),
                url=__file__
            )
        finally:
            consumer.channel.basic_ack(msg.method.delivery_tag)
            time.sleep(1)

if __name__ == "__main__":
    run()