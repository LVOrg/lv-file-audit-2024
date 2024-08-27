import typing

import cy_docs
import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.repository import Repository
from cyx.cloud.mail_services import MailService
from cyx.cloud.drive_services import DriveService
from cyx.cloud.cloud_file_sync_service import FileSync


class CloudServiceUtils:
    memcache_service: MemcacheServices = cy_kit.singleton(MemcacheServices)
    mail_service: MailService = cy_kit.singleton(MailService)
    drive_service: DriveService = cy_kit.singleton(DriveService)
    file_sync: FileSync = cy_kit.singleton(FileSync)
    def __init__(self):

        self.cache_key = f"{type(self).__module__}/{type(self).__name__}/check-ready"

    def cache_delete(self, app_name):
        ret = self.memcache_service.get_dict(self.cache_key)
        if isinstance(ret, dict):
            if ret.get(app_name):
                del ret[app_name]
            self.memcache_service.set_dict(self.cache_key, ret)

    def is_ready_for(self, app_name, cloud_name):
        ret = self.memcache_service.get_dict(self.cache_key)
        if not isinstance(ret, dict):
            ret = {}
        if ret.get(app_name) is None:
            db_context = Repository.apps.app("admin")
            item = db_context.context.aggregate().match(
                Repository.apps.fields.Name == app_name
            ).project(
                cy_docs.fields.secret_key >> getattr(Repository.apps.fields.AppOnCloud, cloud_name).ClientSecret
            ).first_item()
            if item is None:
                ret[app_name] = False
            else:
                ret[app_name] = item.secret_key is not None
            self.memcache_service.set_dict(self.cache_key, ret)
        return ret[app_name]

    def do_sync_data(self, app_name: str, cloud_name: str, upload_item):
        return self.file_sync.do_sync(
            app_name=app_name,
            cloud_name=cloud_name,
            upload_item=upload_item

        )

    def get_cloud_name_of_upload(self, upload_item=None, app_name: str=None, upload_id=None) -> typing.Tuple[str | None, dict | None]:
        """
        Detect location of  resource is 'Google' ,"Azure' or 'AWS'
        :param app_name:
        :param upload_id:
        :return:
        """
        if upload_item is None:
            upload_item = Repository.files.app(app_name).context.find_one(
                Repository.files.fields.Id == upload_id
            )
        if upload_item is None:
            return None, dict(
                Code="ItemWasNotFound",
                Message=f"{upload_id} was not found in {app_name}"
            )
        if upload_item[Repository.files.fields.StorageType] == "google-drive":
            return "Google", None
        if upload_item[Repository.files.fields.StorageType] == "onedrive":
            return "Azure", None
        if upload_item[Repository.files.fields.StorageType] == "s3":
            return "AWS", None
        else:
            return "local",None
