from cyx.common import config
from cyx.common.brokers import Broker
import cy_kit
import cyx.common.msg
import cy_utils
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
from gradio_client import Client
import os
from cyx.processing_file_manager_services import ProcessManagerService
class ImageService:
    def __init__(self,
                 broker=cy_kit.singleton(Broker),
                 local_api_service = cy_kit.singleton(LocalAPIService),
                 process_manager_service=cy_kit.singleton(ProcessManagerService)
                 ):
        self.process_services_host = config.process_services_host or "http://localhost"
        self.broker = broker
        self.local_api_service = local_api_service
        self.process_manager_service = process_manager_service


