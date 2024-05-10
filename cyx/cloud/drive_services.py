import typing

import cy_kit
from cyx.cloud.drive_service_google import DriveServiceGoogle
from cyx.cloud.drive_service_ms import DriveServiceMS
class DriveService:
    def __init__(self,
                 drive_service_google:DriveServiceGoogle=cy_kit.singleton(DriveServiceGoogle),
                 drive_service_ms:DriveServiceMS = cy_kit.singleton(DriveServiceMS)

                 ):
        self.drive_service_google = drive_service_google
        self.drive_service_ms = drive_service_ms

    def get_available_space(self, app_name, cloud_name:str)->typing.Tuple[int|None,dict|None]:
        """
        get available space of Google Drive
        :param app_name:
        :return: size, error
        """
        if cloud_name=="Google":
            return self.drive_service_google.get_available_space(app_name)
        elif cloud_name=="Azure":
            return self.drive_service_ms.get_available_space(app_name)

