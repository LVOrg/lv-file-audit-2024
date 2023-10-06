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
from cy_xdoc.services.apps import AppServices,AppsCacheService
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
    def __init__(self, request: Request):
        self.request = request
