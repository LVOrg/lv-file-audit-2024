import datetime

import cy_kit
from cyx.cloud.cloud_file_sync_service_azure import CloudFileSyncServiceAzure
from cyx.cloud.cloud_file_sync_service_google import CloudFileSyncServiceGoogle
from cyx.repository import Repository
from cyx.common.brokers import Broker
from cyx.common import msg
class FileSync:
    def __init__(self,
                 azure:CloudFileSyncServiceAzure=cy_kit.singleton(CloudFileSyncServiceAzure),
                 google: CloudFileSyncServiceGoogle=cy_kit.singleton(CloudFileSyncServiceGoogle),
                 msg:Broker = cy_kit.singleton(Broker)
                 ):
        self.azure=azure
        self.google=google
        self.msg = msg
    def do_sync(self, app_name:str, cloud_name:str, upload_item):
        cloud_file_sync_content=Repository.cloud_file_sync.app(app_name=app_name)
        cloud_file_sync_item = cloud_file_sync_content.context.find_one(
            cloud_file_sync_content.fields.UploadId==upload_item.Id
        )
        if cloud_file_sync_item:
            print("Update")
        else:
            Repository.cloud_file_sync.app(app_name=app_name).context.insert_one(
                Repository.cloud_file_sync.fields.SyncCount<<0,
                Repository.cloud_file_sync.fields.CloudName << cloud_name,
                Repository.cloud_file_sync.fields.UploadId<< upload_item.Id,
                Repository.cloud_file_sync.fields.CreatedOn<< datetime.datetime.utcnow(),
                Repository.cloud_file_sync.fields.IsError<<False
            )
        if cloud_name == "Google":

            self.msg.emit(
                app_name=app_name,
                message_type=msg.MSG_CLOUD_GOOGLE_DRIVE_SYNC,
                data=upload_item)
        elif cloud_name == "Azure":
            self.msg.emit(
                app_name=app_name,
                message_type=msg.MSG_CLOUD_ONE_DRIVE_SYNC,
                data=upload_item)
        elif cloud_name == "AWS":
            self.msg.emit(
                app_name=app_name,
                message_type=msg.MSG_CLOUD_S3_SYNC,
                data=upload_item)
        # if file_size>512*1024:
        #
        #     else:
        #         raise NotImplemented(f"{cloud_name} was not support")
        #     return
        #
        #
        #
        # try:
        #     if cloud_name=="Google":
        #         self.google.do_sync(app_name,upload_item)
        #
        #     elif cloud_name=="Azure":
        #         self.azure.do_sync(app_name,upload_item)
        #     else:
        #         raise NotImplemented(f"{cloud_name} was not support")
        # except Exception as ex:
        #     Repository.cloud_file_sync.app(app_name=app_name).context.update(
        #         Repository.cloud_file_sync.fields.UploadId==upload_item.Id,
        #         Repository.cloud_file_sync.fields.IsError << True,
        #         Repository.cloud_file_sync.fields.ErrorContent << repr(ex),
        #     )
