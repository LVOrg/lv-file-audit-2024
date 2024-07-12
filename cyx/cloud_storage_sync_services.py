import cy_kit
from cyx.cloud.cloud_service_utils import CloudServiceUtils


class CloudStorageSyncService:
    def __init__(self, cloud_service_utils=cy_kit.singleton(CloudServiceUtils)):
        self.map = {
            "onedrive": "Azure",
            "google-drive": "Google",
            "s3": "AWS"
        }
        self.cloud_service_utils = cloud_service_utils

    def do_sync(self, app_name, upload_item):
        if self.map.get(upload_item.StorageType):
            self.cloud_service_utils.do_sync_data(
                app_name=app_name,
                cloud_name=self.map.get(upload_item.StorageType),
                upload_item=upload_item

            )
