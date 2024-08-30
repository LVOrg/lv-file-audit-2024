import hashlib
import os
import sys
import pathlib

import traceback



sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
sys.path.append("/app")

import cyx.common.msg
import mimetypes
import cy_kit
from icecream import ic
from cyx.rabbit_utils import Consumer, MesssageBlock
import time
import gc

from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongodb_service = cy_kit.singleton(LogsToMongoDbService)
from cyx.local_api_services import LocalAPIService
local_pai_service = cy_kit.singleton(LocalAPIService)
from cyx.file_utils_services import FileUtilService
file_util_service = cy_kit.singleton(FileUtilService)
from cyx.repository import Repository
from cyx.remote_caller import RemoteCallerService
remote_caller_service = cy_kit.singleton(RemoteCallerService)
from tika import parser
from cyx.common import config
from tqdm import tqdm
import urllib.parse
import requests
import typing
__tem_dir__ = "/tmp/__download_file__"
os.makedirs(__tem_dir__,exist_ok=True)
def download_file_with_progress(url, filename)->typing.Tuple[str|None,dict|None]:
  """
  Downloads a file from the given URL with a progress bar.

  Args:
      url (str): URL of the file to download.
      filename (str): Name of the file to save locally.

  Raises:
      Exception: If an error occurs during download.
  """

  # Create response object

  response = requests.get(url, stream=True,verify=False)

  # Check for successful response
  if response.status_code >= 200  and response.status_code<300:
    # Get file size
    total_size = int(response.headers.get('content-length', 0))

    # Create progress bar
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)

    with open(filename, 'wb') as file:
      for data in response.iter_content(chunk_size=1024):
        progress_bar.update(len(data))
        file.write(data)

    progress_bar.close()
    print(f"File '{filename}' downloaded successfully.")
    return filename,None
  else:
    return None, dict(code=f"{response.status_code}",message=response.text)
from cyx.common.rabitmq_message import RabitmqMsg
broker = cy_kit.singleton(RabitmqMsg)
broker.emit(app_name="xxxx",message_type=cyx.common.msg.MSG_EXTRACT_TEXT_FROM_OFFICE_FILE,data={})
def run():
    consumer = Consumer(cyx.common.msg.MSG_EXTRACT_TEXT_FROM_OFFICE_FILE)

    while True:
        time.sleep(1)
        try:
            gc.collect()
            msg = consumer.get_msg(delete_after_get=False)
            if isinstance(msg, MesssageBlock):
                if msg.data == {}:
                    consumer.channel.basic_ack(
                        msg.method.delivery_tag
                    )
                    continue
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

                url_resource ,_,_,_,_ = local_pai_service.get_download_path(
                    upload_item = upload_item,
                    app_name = app_name

                )
                file_name = hashlib.sha256(url_resource.encode()).hexdigest()
                download_file = os.path.join(__tem_dir__,file_name)
                download_file_with_progress(url_resource,download_file)

                ic(url_resource)


                ic(msg.data[Repository.files.fields.FullFileNameLower.__name__])


        except:
            logs_to_mongodb_service.log(
                error_content=traceback.format_exc(),
                url=__file__
            )
        finally:
            gc.collect()
if __name__ =="__main__":
    run()