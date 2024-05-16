import time

import cy_kit
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.msg import broker
from cyx.common.share_storage import ShareStorageService
msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.temp_file import TempFiles
temp_file = cy_kit.singleton(TempFiles)
# from cyx.loggers import LoggerService
from cyx.content_services import ContentService,ContentTypeEnum
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
import  cy_utils
import cy_utils.texts
import mimetypes
from cy_xdoc.services.search_engine import SearchEngine
import gradio_client
print(gradio_client.__version__)
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
from gradio_client import Client
from cyx.processing_file_manager_services import ProcessManagerService
from cyx.google_drive_utils.directories import GoogleDirectoryService
from cyx.common import config
import cy_file_cryptor.context
from kazoo.client import KazooClient
from memcache import Client as MClient
import requests
def check_memcache():
    ok = False
    while not  ok:
        try:
            cache_server = config.cache_server
            print(f"Connect to {cache_server}")
            client = MClient(tuple(cache_server.split(":")))
            ok = client.set("test","ok")
        except Exception as e:
            print(f"Error connecting to Memcached: {e}")
    print(f"Memcache server is ok run on {config.cache_server}")
def check_zookeeper():
    distribute_lock_server = config.distribute_lock_server
    ok = False
    while not ok:
        try:
            # Connect to Zookeeper
            zk = KazooClient(distribute_lock_server)
            zk.start()
            ok = True

        except Exception as e:
            print(f"Error connecting to Zookeeper: {e}")

        finally:
            # Close the Kazoo client connection
            zk.stop()
    print(f"zookeeper is ok {distribute_lock_server}")
def check_url(url,method="get"):
    response = getattr(requests,method)(url)
    while response.status_code!=200:
        print(f"{url} is unavailable")
        print("re-connect on next 5 seconds")
        time.sleep(5)
        response = getattr(requests,method)(url)
    print(f"{url} is available")
check_url("https://api.trogiupluat.vn/swagger/index.html")
check_memcache()
check_zookeeper()
cy_file_cryptor.context.set_server_cache(config.cache_server)
import cy_file_cryptor.wrappers
class JobLibs:
    shared_storage_service:ShareStorageService = cy_kit.singleton(ShareStorageService)
    content_service:ContentService = cy_kit.singleton(ContentService)
    # logger=cy_kit.singleton(LoggerService),
    local_api_service:LocalAPIService = cy_kit.singleton(LocalAPIService)
    search_engine = cy_kit.singleton(SearchEngine)
    process_manager_service:ProcessManagerService = cy_kit.singleton(ProcessManagerService)
    azure_utils_services:AzureUtilsServices = cy_kit.singleton(AzureUtilsServices)
    google_directory_service:GoogleDirectoryService = cy_kit.singleton(GoogleDirectoryService)

    @staticmethod
    def get_doc_type(file_ext: str) -> str:
        file_ext = file_ext.lower()
        mime_type, _ = mimetypes.guess_type(f"a.{file_ext}")
        if mime_type.startswith("image/"):
            return "image"
        elif file_ext.lower() == "pdf":
            return "pdf"
        elif mime_type.startswith("video/"):
            return "video"
        elif file_ext in config.ext_office_file:
            return "office"
        else:
            return "unknown"

    @staticmethod
    def do_process_content(action_info:dict,download_url:str,download_file:str):
        """
        Call external service for content processing
        :param action_info:
        :param download_url:
        :param download_file:
        :exception cy_utils.CallAPIException
        :return:
        """

        action = action_info['content']
        content= None
        if action['type'] == 'tika':
            content = cy_utils.call_local_tika(
                action=action,
                action_type="content",
                url_file=download_url,
                download_file=""
            )
        elif action['type'] == 'web-api':
            content = cy_utils.call_web_api(
                data=action,
                action_type="content",
                url_file=download_url,
                download_file=download_file
            )
        return content