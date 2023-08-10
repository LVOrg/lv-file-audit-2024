"""
This Consumer detect any image if it has table or tabular format and generate data
Consumer  này phát hiện bất kỳ hình ảnh nào nếu nó có định dạng bảng hoặc dạng bảng và tạo dữ liệu
"""
import pathlib
import sys
import os

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.share_storage import ShareStorageService
import cyx.document_layout_analysis.system
cyx.document_layout_analysis.system.set_offline_dataset(False)
shared_storage_service = cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_dataset_path(
    os.path.abspath(
        os.path.join(shared_storage_service.get_root(), "dataset")
    )
)
from cyx.common.msg import MSG_FILE_DOC_LAYOUT_ANALYSIS, broker, MessageService

from cyx.common.msg import MessageInfo
from cyx.common.audio_utils import AudioService
from cyx.common.temp_file import TempFiles
from cyx.document_layout_analysis.table_ocr_service import TableOCRService
from cy_xdoc.services.search_engine import SearchEngine

shared_storage_service=shared_storage_service
audio_service=cy_kit.singleton(AudioService)
temp_file=cy_kit.singleton(TempFiles)
table_ocr_service=cy_kit.singleton(TableOCRService)
search_engine = cy_kit.singleton(SearchEngine)
test_dir = pathlib.Path(__file__).parent.__str__()
test_file = os.path.join(test_dir,"doremon8.jpg")
analyze_image_by_file_path = table_ocr_service.analyze_image_by_file_path
analyze_image_by_file_path(test_file,os.path.join(test_dir,"r.jpg"))
@broker(message=MSG_FILE_DOC_LAYOUT_ANALYSIS)
class Process:
    def __init__(self):
        print("consumer init")
        self.shared_storage_service = shared_storage_service
        self.audio_service = audio_service
        self.temp_file = temp_file

        self.output_dir = self.shared_storage_service.get_temp_dir(self.__class__)
        self.table_ocr_service = table_ocr_service
        self.search_engine = search_engine

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        print("Receive mssage")
        print(f"app = {msg_info.AppName}")
        print(f'id = {msg_info.Data["_id"]}')

        full_file_path = self.temp_file.get_path(
            app_name=msg_info.AppName,
            file_ext=msg_info.Data["FileExt"],
            upload_id=msg_info.Data["_id"]

        )

        if full_file_path is None:
            print("File not found")
            msg_broker.delete(msg_info)
            return

        import mimetypes
        mime_type, _ = mimetypes.guess_type(full_file_path)
        if mime_type.startswith('image/'):
            print(f"Process layout {full_file_path}")
            output_file_path = os.path.join(self.output_dir, f'{msg_info.Data["_id"]}.{msg_info.Data["FileExt"]}')
            ret = self.table_ocr_service.analyze_image_by_file_path(
                input_file_path=full_file_path,
                ouput_file_path=output_file_path
            )
            print(ret.result_image_path)
            print(ret.text)
            print(ret.table)
            self.search_engine.update_data_field(
                app_name= msg_info.AppName,
                id=msg_info.Data["_id"],
                field_path="doc_layout_analysis_data",
                field_value= dict(
                    text = ret.text,
                    table = ret.table
                )

            )

            print(f"Update search_engine is ok")

        if mime_type.startswith('video/'):
            msg_info.Data["processing_file"] = full_file_path
            msg_broker.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_EXTRACT_AUDIO_FROM_VIDEO,
                data=msg_info.Data
            )
