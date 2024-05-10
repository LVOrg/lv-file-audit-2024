import cy_docs
import cy_kit
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.repository import Repository
from cyx.cloud.mail_services import MailService
from cyx.cloud.drive_services import DriveService
from cyx.cloud.cloud_file_sync_service import FileSync
class CloudServiceUtils:
    def __init__(self,
                 memcache_service: MemcacheServices = cy_kit.singleton(MemcacheServices),
                 mail_service: MailService = cy_kit.singleton(MailService),
                 drive_service: DriveService = cy_kit.singleton(DriveService),
                 file_sync:FileSync = cy_kit.singleton(FileSync)
                 ):
        self.memcache_service = memcache_service
        self.mail_service = mail_service
        self.drive_service = drive_service
        self.file_sync = file_sync
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

    def do_sync_data(self, app_name:str, cloud_name:str,upload_item):
        return self.file_sync.do_sync(
            app_name=app_name,
            cloud_name=cloud_name,
            upload_item=upload_item

        )
