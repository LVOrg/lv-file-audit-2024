import cy_kit
from cyx.easy_ocr import EasyOCRService
es=cy_kit.singleton(EasyOCRService)
fx=es.get_text("/home/vmadmin/python/cy-py/a_checking/resources/26760_ram_kingston_laptop_1_1.jpg")
print(fx)
