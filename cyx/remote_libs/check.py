import cy_kit
from cyx.remote_libs.office_services import OfficeService
office_service:OfficeService= cy_kit.singleton(OfficeService)
office_service.get_image_of_file(host="http://172.16.13.72:8001",file_path=f"/home/vmadmin/python/cy-py/cy_libs/office.py")