import sys
import pathlib
working_path = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_path)
import  cy_kit
from cyx.document_layout_analysis.doctr_service import DoctrService
doc_tr_service = cy_kit.singleton(DoctrService)
img_src= "/home/vmadmin/python/v6/file-service-02/open-cv-source/hinh_1.jpg"
f=doc_tr_service.get_result_from_image(img_src)
print(f)