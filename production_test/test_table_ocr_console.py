import sys
import pathlib

working_path = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_path)

import cyx.document_layout_analysis.system
cyx.document_layout_analysis.system.set_offline_dataset(True)
cyx.document_layout_analysis.system.set_dataset_path("./dataset")
import transformers.file_utils
transformers.file_utils.is_pytesseract_available()
import cy_kit
from  cyx.document_layout_analysis.table_ocr_service import TableOCRService
f=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.png"
fo=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_4.png"
table_ocr_service = cy_kit.singleton(TableOCRService)
import deepdoctection.extern.model

ret=table_ocr_service.analyze_image_by_file_path(
    input_file_path=f,
    ouput_file_path=fo
)
for x in ret:
    if isinstance(x,str):
        print(x)
    else:
        print(type(x))