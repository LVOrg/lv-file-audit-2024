import datetime
import traceback
from cyx.common import config
from cyx.common import get_doc_type
from cyx.common.brokers import Broker
import cy_kit
import cyx.common.msg
import cy_utils
from cyx.local_api_services import LocalAPIService
from cyx.repository import Repository
import cy_utils.texts
from cy_xdoc.services.search_engine import SearchEngine
from cyx.processing_file_manager_services import ProcessManagerService
class ExtractContentService:
    def __init__(self,
                 broker = cy_kit.singleton(Broker),
                 local_api_service = cy_kit.singleton(LocalAPIService),
                 search_engine=cy_kit.singleton(SearchEngine),
                 process_manager_service = cy_kit.singleton(ProcessManagerService)):
        self.process_services_host = config.process_services_host or "http://localhost"
        self.broker = broker
        self.local_api_service = local_api_service
        self.search_engine = search_engine
        self.process_manager_service = process_manager_service

    def save_search_engine(self, data,app_name)->str|None:
        try:
            download_url, rel_path, file_name, token, lolca_share_id = self.local_api_service.get_download_path(
                upload_item= data,
                app_name = app_name
            )
            doc_type = cyx.common.get_doc_type(file_name)
            if not hasattr(config.process_services,doc_type):
                """
                Undeclared action exit
                """
                return None

            action_data = getattr(config.process_services,doc_type)
            if not hasattr(action_data,"content"):
                """
                Undeclared action content fot this media type
                """
                return None

            action = getattr(action_data,"content")
            content = None
            if action.get('type')=="tika":
                content = cy_utils.call_local_tika(
                    action=action,
                    action_type="content",
                    url_file=download_url,
                    download_file=""
                )
            if action.get('type') == "web-api":
                content = cy_utils.call_web_api(
                    data = action,
                    action_type="content",
                    url_file= download_url,
                    download_file = file_name

                )

            if isinstance(content,str):
                self.do_update_content(
                    data= data,
                    content=content,
                    app_name=app_name
                )
            print("update content is OK")
            self.process_manager_service.submit(
                data=data,
                app_name=app_name,
                action_type="content"
            )

        except Exception as ex:
            self.process_manager_service.submit_error(
                data=data,
                app_name=app_name,
                action_type="content",
                error= ex
            )
            self.broker.emit(
                app_name=app_name,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT,
                data=data
            )

    def get_from_tika(self, action):
        pass

    def do_update_content(self, data,app_name, content):
        content = cy_utils.texts.well_form_text(content)
        self.search_engine.update_content(
            app_name=app_name,
            id=data.id,
            content=content,
            replace_content=True,
            data_item=data
        )
