import sys
import pathlib
import  os
working_path = pathlib.Path(__file__).parent.parent.parent.__str__()
sys.path.append(working_path)
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
# cyx.document_layout_analysis.system.set_dataset_path("./dataset")
import transformers.file_utils
transformers.file_utils.is_pytesseract_available()

from  cyx.document_layout_analysis.table_ocr_service import TableOCRService
f=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.png"
fo=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_4.png"
table_ocr_service = cy_kit.singleton(TableOCRService)
import deepdoctection.extern.model

ret=table_ocr_service.analyze_image_by_file_path(
    input_file_path=f,
    ouput_file_path=fo
)
print(ret.table)
print(ret.text)

print(ret.result_image_path)