import cy_kit
from cyx.g_drive_services import GDriveService
g= cy_kit.singleton(GDriveService)
token = g.get_access_token_from_refresh_token("lv-docs")
svc=  g.get_service_by_token("lv-docs",token)
print(svc)