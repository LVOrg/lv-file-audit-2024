import cy_kit
from cyx.g_drive_services import GDriveService
class DriveServiceGoogle:
    def __init__(self, g_drive_service:GDriveService = cy_kit.singleton(GDriveService)):
        self.g_drive_service= g_drive_service

    def get_available_space(self, app_name):
        """
        nếu người dùng có bộ nhớ không giới hạn return None, None

        :param app_name:
        :return:
        """
        service, error = self.g_drive_service.get_service_by_app_name(app_name=app_name, g_service_name="v3/drive")
        if error:
            return None, error
        fields = 'quotaBytesTotal,quotaBytesUsed'
        about = service.about().get(fields="storageQuota").execute()
        if not about.get("storageQuota").get("limit"):
            return None,None
        else:
            return int(about.get("storageQuota").get("limit"))-int(about.get('storageQuota').get('usage')), None

