import cy_kit
from cyx.lv_ocr_services import LVOCRService
ocr= cy_kit.singleton(LVOCRService)
ret = ocr.do_orc(
    file_path = "/home/vmadmin/python/cy-py/a-working/test-huy/mho-hc - thông báo quy định về đồng phục mavin - toàn thể cbnv mavin _1_.pdf"

)
print(ret)