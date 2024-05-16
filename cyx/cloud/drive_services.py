import typing

import cy_kit
from cyx.cloud.drive_service_google import DriveServiceGoogle
from cyx.cloud.drive_service_ms import DriveServiceMS
from cyx.repository import Repository


class DriveService:
    """
    Serve for google-drive and ms onedrive on ly
    """

    def __init__(self,
                 drive_service_google: DriveServiceGoogle = cy_kit.singleton(DriveServiceGoogle),
                 drive_service_ms: DriveServiceMS = cy_kit.singleton(DriveServiceMS)

                 ):
        self.drive_service_google = drive_service_google
        self.drive_service_ms = drive_service_ms

    def get_available_space(self, app_name, cloud_name: str) -> typing.Tuple[int | None, dict | None]:
        """
        get available space of Google Drive
        :param app_name:
        :return: size, error
        """
        if cloud_name == "Google":
            return self.drive_service_google.get_available_space(app_name)
        elif cloud_name == "Azure":
            return self.drive_service_ms.get_available_space(app_name)
        else:
            return None, dict(Code="NotSupport", Message=f"{cloud_name} did not bestow {app_name}")

    def remove_upload(self, app_name: str, cloud_name: str, upload_id: str) -> typing.Tuple[bool, dict | None]:
        """
        Delete Resource on cloud by upload_id
        The method will find in mongodb UploadItem with upload_id
        if UploadItem has CloudId (ResourceId of content on cloud such as Google Onedrive or S3)
        Will perform delete resource
        :param app_name:
        :param cloud_name:
        :param upload_id:
        :return:
        """
        upload_item = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.Id == upload_id
        )
        if not upload_item:
            return False, None
        if upload_item[Repository.files.fields.CloudId] is None:
            return False, None
        if cloud_name == "Google":
            ret, error = self.drive_service_google.remove_upload(app_name=app_name,
                                                                 file_id=upload_item[Repository.files.fields.CloudId])
            if error:
                return False, error
            else:
                return ret, None
        elif cloud_name == "Azure":
            ret, error = self.drive_service_ms.remove_upload(app_name=app_name,
                                                             file_id=upload_item[Repository.files.fields.CloudId])
            if error:
                return False, error
            else:
                return ret, None
        else:
            return False, dict(Code="NotSupport", Message=f"{cloud_name} did not bestow {app_name}")
