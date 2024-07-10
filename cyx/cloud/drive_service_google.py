import typing
import json
import cy_kit
from cyx.g_drive_services import GDriveService
import googleapiclient.errors
class DriveServiceGoogle:
    def __init__(self, g_drive_service:GDriveService = cy_kit.singleton(GDriveService)):
        self.g_drive_service= g_drive_service

    def get_available_space(self, app_name):
        """
        nếu người dùng có bộ nhớ không giới hạn return None, None

        :param app_name:
        :return:
        """
        try:
            # info,error = self.g_drive_service.get_access_token_from_access_token(app_name )

            service, error = self.g_drive_service.get_service_by_app_name(app_name=app_name, g_service_name="v3/drive")
            if error:
                return None, error
            fields = 'quotaBytesTotal,quotaBytesUsed'
            about = service.about().get(fields="storageQuota").execute()
            if not about.get("storageQuota").get("limit"):
                return None,None
            else:
                return int(about.get("storageQuota").get("limit"))-int(about.get('storageQuota').get('usage')), None
        except googleapiclient.errors.HttpError as ex:
            try:
                # info, error = self.g_drive_service.get_access_token_from_access_token(app_name,nocache=True)
                service, error = self.g_drive_service.get_service_by_app_name(app_name=app_name, g_service_name="v3/drive",from_cache=False)
                if error:
                    return None, error
                fields = 'quotaBytesTotal,quotaBytesUsed'
                about = service.about().get(fields="storageQuota").execute()
                if not about.get("storageQuota").get("limit"):
                    return None, None
                else:
                    return int(about.get("storageQuota").get("limit")) - int(about.get('storageQuota').get('usage')), None
            except googleapiclient.errors.HttpError as ex:
                error = json.loads(ex.content.decode())
                if error.get("error"):
                    error=error.get("error")
                return None,dict(Code=error.get("code"),Message=error.get("message"))

    def remove_upload(self, app_name, file_id)->typing.Tuple[bool,dict|None]:
        """
        Delete file in Google by file_id
        :param app_name:
        :param file_id:
        :return:
        """
        service, error = self.g_drive_service.get_service_by_app_name(app_name)
        if error:
            return  False,error
        try:
            res =service.files().delete(fileId=file_id).execute()
            return True,None
        except googleapiclient.errors.HttpError as ex:
            try:
                res =json.loads(ex.content.decode())
                if isinstance(res.get('error'),dict):
                    return False, dict(Code=res.get('error').get('code'), Message=res.get('error').get('message'))
                else:
                    return False, dict(Code="ErrorFromGoogle", Message=ex.content.decode())
            finally:
                if ex.status_code!=404:
                    return False, dict(Code="ErrorFromGoogle", Message=ex.content.decode())
                return True,None
        except Exception as ex:
            return False, dict(Code="Error",Message= repr(ex))


