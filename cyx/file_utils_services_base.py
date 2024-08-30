import cy_kit
from cyx.common import config
from cyx.db_models.files import DocUploadRegister
from cyx.cloud.cloud_service_utils import CloudServiceUtils
from cyx.elastic_search_utils_service import ElasticSearchUtilService
from cyx.cloud_storage_sync_services import CloudStorageSyncService
from cyx.local_api_services import LocalAPIService
from cyx.extract_content_service import ExtractContentService
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.g_drive_services import GDriveService
from cyx.common.file_storage_mongodb import MongoDbFileService
from cyx.remote_caller import RemoteCallerService
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
class BaseUtilService:
    config = config
    """
    All config of app here
    """
    memcache_service = cy_kit.singleton(MemcacheServices)
    """
    Cache service
    """
    g_drive_service: GDriveService = cy_kit.singleton(GDriveService)
    cloud_service_utils: CloudServiceUtils = cy_kit.singleton(CloudServiceUtils)
    elastic_search_util_service: ElasticSearchUtilService = cy_kit.singleton(ElasticSearchUtilService)
    cloud_storage_sync_service: CloudStorageSyncService = cy_kit.singleton(CloudStorageSyncService)
    local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService)
    extract_content_service: ExtractContentService = cy_kit.singleton(ExtractContentService)
    cache_type= f"{DocUploadRegister.__module__}.{DocUploadRegister.__name__}"
    mongo_db_file_service = cy_kit.singleton(MongoDbFileService)
    remote_caller_service = cy_kit.singleton(RemoteCallerService)
    logs_to_mongodb_service = cy_kit.singleton(LogsToMongoDbService)
