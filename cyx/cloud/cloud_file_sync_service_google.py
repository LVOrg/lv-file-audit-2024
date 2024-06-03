import cy_kit
from cyx.g_drive_services import GDriveService
from cyx.google_drive_utils.directories import GoogleDirectoryService
class CloudFileSyncServiceGoogle:
    def __init__(self,
                 g_drive_service:GDriveService=cy_kit.singleton(GDriveService),
                 google_directory_service:GoogleDirectoryService = cy_kit.singleton(GoogleDirectoryService)
                 ):
        self.g_drive_service = g_drive_service
        self.google_directory_service = google_directory_service
    def do_sync(self, app_name, upload_item):
        self.g_drive_service.sync_to_drive(
            app_name = app_name,
            upload_item = upload_item
        )