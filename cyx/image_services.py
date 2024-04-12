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

    def generate_image(self, data, app_name):
        try:
            download_url, rel_path, file_name, token, local_share_id = self.local_api_service.get_download_path(
                upload_item=data,
                app_name=app_name
            )
            doc_type = cyx.common.get_doc_type(file_name)
            if not hasattr(config.process_services, doc_type):
                """
                Undeclared action exit
                """
                return None

            action_data = getattr(config.process_services, doc_type)
            if not hasattr(action_data, "image"):
                """
                Undeclared action content fot this media type
                """
                return None
            action = getattr(action_data,"image")
            if action.get('type')=="socat":
                client = Client(f"{self.process_services_host}:{action.get('port')}/")
                _, result = client.predict(
                    download_url,
                    False,
                    api_name="/predict"
                )
                image_file_path = f"{rel_path}.png"
                if os.path.isfile(result):
                    self.local_api_service.send_file(
                        file_path=result,
                        token=token,
                        local_share_id=local_share_id,
                        app_name= app_name,
                        rel_server_path=image_file_path

                    )
                    if os.path.isfile(result):
                        os.remove(result)
                    print(f"update image for {rel_path}")
            else:
                raise  NotImplemented()
            self.process_manager_service.submit(
                data= data,
                app_name =app_name,
                action_type= "image"
            )
        except Exception as ex:
            self.process_manager_service.submit_error(
                data=data,
                app_name=app_name,
                action_type="image",
                error= ex
            )
            self.broker.emit(
                app_name=app_name,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE,
                data=data
            )
