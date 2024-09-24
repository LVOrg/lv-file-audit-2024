
import os.path

import typing
from urllib.error import HTTPError

from cyx.common import config

from cyx.common.brokers import Broker
import cy_kit
import cyx.common.msg
import cy_utils
from cyx.local_api_services import LocalAPIService
from retry import retry

import cy_utils.texts
from cy_xdoc.services.search_engine import SearchEngine
from cyx.processing_file_manager_services import ProcessManagerService
from cyx.malloc_services import MallocService
import  requests
class ExtractContentService:
    broker = cy_kit.singleton(Broker)
    local_api_service = cy_kit.singleton(LocalAPIService)
    search_engine = cy_kit.singleton(SearchEngine)
    process_manager_service = cy_kit.singleton(ProcessManagerService)
    malloc_service = cy_kit.singleton(MallocService)
    process_services_host = config.process_services_host or "http://localhost"
    def save_search_engine(self, data,app_name)->typing.Union[str ,None]:
        if config.elastic_search == False:
            return
        try:
            self.broker.emit(
                app_name=app_name,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT,
                data=data
            )
            # download_url, rel_path, file_name, token, lolca_share_id = self.local_api_service.get_download_path(
            #     upload_item= data,
            #     app_name = app_name
            # )
            # doc_type = cyx.common.get_doc_type(file_name)
            # if doc_type=="image":
            #     self.broker.emit(
            #         app_name=app_name,
            #         message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT,
            #         data=data
            #     )
            #     return
            #
            # print("update content is OK")
            # if doc_type=="office":
            #     self.update_by_using_tika(
            #         download_url=download_url,
            #         rel_path=rel_path,
            #         data=data,
            #         app_name=app_name
            #     )
            #     self.process_manager_service.submit(
            #         data=data,
            #         app_name=app_name,
            #         action_type="content"
            #     )
            # if doc_type=="pdf":
            #     self.broker.emit(
            #         app_name=app_name,
            #         message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT,
            #         data=data
            #     )
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
        finally:
            self.malloc_service.reduce_memory()

    def get_from_tika(self, action):
        pass

    def do_update_content(self, data,app_name, content):
        try:
            content = cy_utils.texts.well_form_text(content)
            self.search_engine.update_content(
                app_name=app_name,
                id=data.id,
                content=content,
                replace_content=True,
                data_item=data
            )
        except Exception as ex:
            raise ex
        finally:
            self.malloc_service.reduce_memory()
    def get_url(self)->str:
        return config.remote_ocr
    def health_check_ocr(self,timeout_in_second: int=2) -> bool:
        """
        Checks the health of the remote OCR service.

        Args:
            timeout_in_second: Maximum time to wait for a response before considering the check failed.

        Returns:
            True if the service is healthy, False otherwise.
        """

        url = f"{config.remote_ocr}/hz"

        try:
            response = requests.get(url, timeout=timeout_in_second)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return True
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"Failed to connect to remote OCR service: {e}")
            return False

    def get_content_from_pdf_ocr(self, tika_server, url_content)->typing.Tuple[typing.Union[str ,None],typing.Union[typing.Union[dict,str] ,None]]:
        data = {
            "tika_server": tika_server,
            "remote_file": url_content
        }
        url = f"{config.remote_ocr}/get-content"
        # Send the POST request
        response = requests.post(url, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return  None, response.content.decode()
        ret_data = response.json()
        if ret_data.get("Error"):
            return None,ret_data.get("Error")
        else:
            return  str( ret_data.get("result","")), None
        # Check for successful response

    def update_by_using_ocr_pdf(self, download_url,  data, app_name):
        tika_server = config.tika_server
        content,error = self.get_content_from_pdf_ocr(tika_server=tika_server,url_content= download_url)
        @retry(tries=5,delay=10)
        def save_es():
            self.do_update_content(
                data=data,
                content=content,
                app_name=app_name
            )
        if not error:
            print(content)
            if isinstance(content, str):
                save_es()
        else:
            raise Exception(error)

    def update_by_using_tika(self,download_url,rel_path,data,app_name):
        try:
            file_path = os.path.join(config.file_storage_path, rel_path)
            # if not os.path.isfile(file_path) and not os.path.isdir(f"{file_path}.chunks"):
            #     print("Fail")

            content = cy_utils.get_content_from_tika(
                url_file=download_url,
                abs_file_path =file_path
            )
            if isinstance(content, str):
                self.do_update_content(
                    data=data,
                    content=content,
                    app_name=app_name
                )
        except Exception as ex:
            raise ex
        finally:
            self.malloc_service.reduce_memory()



