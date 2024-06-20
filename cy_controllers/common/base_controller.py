from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response,
    UploadFile,
    Form, File
)
from cy_xdoc.auths import Authenticate
import cy_kit
from cy_xdoc.services.files import FileServices

from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cy_docs
import cyx.common.msg

from cyx.common.file_storage_mongodb import (
    MongoDbFileService, MongoDbFileStorage
)
from cyx.common.mongo_db_services import MongodbService
from cyx.cache_service.memcache_service import MemcacheServices
from cyx.loggers import LoggerService
from fastapi import APIRouter, Depends
from fastapi_router_controller import Controller
from cyx.common.file_cacher import FileCacherService
from fastapi.responses import FileResponse
import mimetypes
import fastapi
import cy_kit
from cyx.common.rabitmq_message import RabitmqMsg
from cy_xdoc.services.apps import AppServices, AppsCacheService
from cy_xdoc.services.search_engine import SearchEngine

# from cyx.media.image_extractor import ImageExtractorService
from cyx.content_manager_services import ContentManagerService
from cyx.thumbs_services import ThumbService
from cyx.common.global_settings_services import GlobalSettingsService
from cyx.gemini_service import GeminiService
from cyx.media.contents import ContentsServices
from cyx.local_api_services import LocalAPIService

from cyx.common.jwt_utils import TokenVerifier
from cyx.local_file_caching_services import LocalFileCachingService
from  cyx.docs_contents_services import DocsContentsServices
from cyx.image_services import ImageService
from cyx.extract_content_service import ExtractContentService
from cyx.g_drive_services import GDriveService
from cyx.distribute_locking.distribute_lock_services import DistributeLockService
from cyx.google_drive_utils.directories import GoogleDirectoryService
from cyx.ms.ms_auth_services import MSAuthService
from cyx.ms.ms_commom_service import MSCommonService
from cyx.cloud.cloud_service_utils import CloudServiceUtils
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
from cyx.cloud.azure.office365_services import MSOffice365Service
from cyx.cloud_cache_services import CloudCacheService
class BaseController:

    msg_service = cy_kit.singleton(RabitmqMsg)
    file_service: FileServices = cy_kit.singleton(FileServices)
    file_storage_service: MongoDbFileService = cy_kit.singleton(MongoDbFileService)
    broker: Broker = cy_kit.singleton(Broker)
    temp_files = cy_kit.singleton(TempFiles)
    memcache_service = cy_kit.singleton(MemcacheServices)
    logger_service = cy_kit.singleton(LoggerService)
    file_cacher_service = cy_kit.singleton(FileCacherService)
    service_app: AppServices = cy_kit.singleton(AppServices)
    apps_cache: AppsCacheService = cy_kit.singleton(AppsCacheService)
    auth_service = cy_kit.singleton(cyx.common.basic_auth.BasicAuth)
    config = cyx.common.config
    search_engine = cy_kit.singleton(SearchEngine)


    mongodb_service = cy_kit.singleton(MongodbService)


    thumb_service: ThumbService = cy_kit.singleton(ThumbService)
    content_manager_service: ContentManagerService = cy_kit.singleton(ContentManagerService)
    global_settings_service: GlobalSettingsService = cy_kit.singleton(GlobalSettingsService)
    gemini_service: GeminiService = cy_kit.singleton(GeminiService)
    # image_extractor_service = cy_kit.singleton(ImageExtractorService)
    tika_contents_service = cy_kit.singleton(ContentsServices)
    local_api_service:LocalAPIService = cy_kit.singleton(LocalAPIService)
    token_verifier: TokenVerifier = cy_kit.singleton(TokenVerifier)
    share_key = cyx.common.config.jwt.secret_key
    local_file_caching_service = cy_kit.singleton(LocalFileCachingService)
    docs_contents_cervices = cy_kit.singleton(DocsContentsServices)
    image_service:ImageService = cy_kit.singleton(ImageService)
    extract_content_service:ExtractContentService = cy_kit.singleton(ExtractContentService)
    g_drive_service:GDriveService = cy_kit.singleton(GDriveService)
    # distribute_lock_service:DistributeLockService = cy_kit.singleton(DistributeLockService)
    google_directory_service:GoogleDirectoryService = cy_kit.singleton(GoogleDirectoryService)
    ms_service:MSAuthService = cy_kit.singleton(MSAuthService)
    ms_common_service:MSCommonService = cy_kit.singleton(MSCommonService)
    cloud_service_utils: CloudServiceUtils = cy_kit.singleton(CloudServiceUtils)
    azure_utils_service: AzureUtilsServices = cy_kit.singleton(AzureUtilsServices)
    ms_office_365_service: MSOffice365Service = cy_kit.singleton(MSOffice365Service)
    cloud_cache_service:CloudCacheService = cy_kit.singleton(CloudCacheService)

    def __init__(self, request: Request):
        self.request = request
