import cy_kit
from cyx.g_drive_services import GDriveService
class CloudFileSyncServiceGoogle:
    def __init__(self, g_drive_service:GDriveService=cy_kit.singleton(GDriveService)):
        self.g_drive_service =g_drive_service
    def do_sync(self, app_name, upload_item):
        self.g_drive_service.sync_to_drive(
            app_name = app_name,
            upload_item = upload_item
        )