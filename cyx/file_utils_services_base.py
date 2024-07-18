import cy_kit
from cyx.common import config
from cy_xdoc.models.files import DocUploadRegister
from cyx.cloud.cloud_service_utils import CloudServiceUtils
from cyx.elastic_search_utils_service import ElasticSearchUtilService
from cyx.cloud_storage_sync_services import CloudStorageSyncService
from cyx.local_api_services import LocalAPIService
from cyx.extract_content_service import ExtractContentService
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.g_drive_services import GDriveService


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
