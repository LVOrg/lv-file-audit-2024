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
from cyx.common.file_storage import FileStorageService
from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cy_docs
import cyx.common.msg
from cyx.common.file_storage_mongodb import (
    MongoDbFileService,MongoDbFileStorage
)

from cyx.cache_service.memcache_service import MemcacheServices
from cyx.loggers import LoggerService
from fastapi import APIRouter,Depends
from fastapi_router_controller import Controller
class BaseController:

    msg_service = cy_kit.singleton(RabitmqMsg)
    file_service: FileServices = cy_kit.singleton(FileServices)
    file_storage_service: MongoDbFileService = cy_kit.singleton(MongoDbFileService)
    msg_service: MessageService = cy_kit.singleton(MessageService)
    broker: Broker = cy_kit.singleton(Broker)
    temp_files = cy_kit.singleton(TempFiles)
    memcache_service = cy_kit.singleton(MemcacheServices)
    logger_service = cy_kit.singleton(LoggerService)

    def __init__(self, request: Request):
        self.request = request