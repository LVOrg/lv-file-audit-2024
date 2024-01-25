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
from cy_fucking_whore_microsoft.services import (
    account_services, ondrive_services
)
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
from cy_fucking_whore_microsoft.services.office_365_services import Office365Service
from cy_fucking_whore_microsoft.fucking_ms_wopi.fucking_wopi_services import FuckingWopiService
# from cyx.media.image_extractor import ImageExtractorService
from cyx.content_manager_services import ContentManagerService
from cyx.thumbs_services import ThumbService
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
    fucking_azure_account_service: account_services.AccountService = cy_kit.singleton(account_services.AccountService)
    fucking_azure_onedrive_service: ondrive_services.OnedriveService = cy_kit.singleton(
        ondrive_services.OnedriveService)
    mongodb_service = cy_kit.singleton(MongodbService)
    fucking_office_365_service = cy_kit.singleton(Office365Service)
    fucking_wopi_service = cy_kit.singleton(FuckingWopiService)

    thumb_service: ThumbService = cy_kit.singleton(ThumbService)
    content_manager_service:ContentManagerService = cy_kit.singleton(ContentManagerService)
    # image_extractor_service = cy_kit.singleton(ImageExtractorService)

    def __init__(self, request: Request):
        self.request = request
