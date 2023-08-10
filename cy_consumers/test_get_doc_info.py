import cy_kit
from cyx.common.file_information import FileInformationService
fx = cy_kit.singleton(FileInformationService)

fx1=f"/home/vmadmin/python/v6/file-service-02/temp-data/lancape.docx"
fx1 =f"/home/vmadmin/python/v6/file-service-02/temp-data/aaaa.xlsx"
fx1=f"/home/vmadmin/python/v6/file-service-02/temp-data/xxxxx.xlsx"
# fx2=f"/home/vmadmin/python/v6/file-service-02/temp-data/lancape.docx"
#
#a = fx.get_total_pages(fx1)
# print(a)

fx.get_pages_content(fx1)