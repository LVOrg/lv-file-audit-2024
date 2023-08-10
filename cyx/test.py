import cy_kit
from cyx.images import ImageServices
from cyx.base import Config
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService
img =  cy_kit.singleton(ImageExtractorService)
svc = cy_kit.singleton(PDFService)
pdf_file = f"/home/vmadmin/python/v6/file-service-02/test-res/tailieu3.pdf"
r1= f"/home/vmadmin/python/v6/file-service-02/test-res/tailieu3.ocr.4.pdf"
r2="/home/vmadmin/python/v6/file-service-02/test-res/tailieu3.4.pdf"
r3=f"/home/vmadmin/python/v6/file-service-02/test-res/image_2.pdf"
r4="/home/vmadmin/python/v6/file-service-02/test-res/Image_2.png"
r5=f"/home/vmadmin/python/v6/file-service-02/test-res/tailieu2.pdf"
r6=f"/home/vmadmin/python/v6/file-service-02/test-res/test001.pdf"
r7="/home/vmadmin/python/v6/file-service-02/test-res/test004.pdf"
r8="/home/vmadmin/python/v6/file-service-02/test-res/test002.pdf"
# pdf_file = img.convert_to_pdf(r8)
ret=  svc.ocr(r8)
print(ret)
fx = svc.get_text(ret)
print(fx)
a,b = svc.get_pdf_searchable_pages(pdf_file)
print(a)
print(b)

ret=  svc.ocr_page_by_page(pdf_file)
print(ret)
# from cyx.media.contents import Contents
# img_service = cy_kit.singleton(
#     ImageServices
# )
# config:Config= cy_kit.singleton(
#     Config
# )
# contents:Contents =cy_kit.singleton(
#     Contents
# )
# config.load("./config.yml")
# img_service.create_thumbs(
#     image_file_path=r"C:\code\python\py_cy\test_resource\img_01.png",
#     size=120
# )
# pdf_path = img_service.convert_to_pdf(image_file_path=r"C:\code\python\py_cy\test_resource\img_01.png")
# a,b = contents.get_text(pdf_path)
# print(a)
