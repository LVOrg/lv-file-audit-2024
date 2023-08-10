import pymongo

import cy_kit
import cyx.common.file_storage

from cy_xdoc.services.apps import AppServices
from cy_xdoc.services.accounts import AccountService

import cy_xdoc.services.files

import cy_xdoc.services.search_engine
import cy_xdoc.services.files
import cy_xdoc.services.apps

import cy_xdoc.services.search_engine
import cy_xdoc.services.accounts
import cy_xdoc.services.secutities
import cyx.common.base
import cyx.common.msg_mongodb
import cyx.common.msg
import cyx.common.file_storage
import cyx.common.file_storage_mongodb

cy_kit.config_provider(
    from_class=cyx.common.file_storage.FileStorageService,
    implement_class=cyx.common.file_storage_mongodb.MongoDbFileService
)
# cy_kit.config_provider(
#     from_class=cy_xdoc.services.file_storage.FileStorageService,
#     implement_class=cy_xdoc.services.file_storage_disk.FileDiskStorageService
# )
"""
Cau hinh luu file dung mongodb
"""
cy_kit.config_provider(
    from_class=cyx.common.msg.MessageService,
    implement_class=cyx.common.msg_mongodb.MessageServiceMongodb
)
"""
Cau hinh he thong msg dung Mongodb
"""
import cyx.common.msg


class Container:
    def __init__(self,
                 data_context: cyx.common.base.DbConnect = cy_kit.singleton(cyx.common.base.DbConnect),
                 service_search: cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(
                     cy_xdoc.services.search_engine.SearchEngine),
                 service_file: cy_xdoc.services.files.FileServices = cy_kit.singleton(
                     cy_xdoc.services.files.FileServices),
                 service_app: cy_xdoc.services.apps.AppServices = cy_kit.singleton(cy_xdoc.services.apps.AppServices),
                 services_msg: cyx.common.msg.MessageService = cy_kit.singleton(
                     cyx.common.msg.MessageService),
                 service_storage: cyx.common.file_storage.FileStorageService = cy_kit.singleton(
                     cyx.common.file_storage.FileStorageService),
                 service_account: cy_xdoc.services.accounts.AccountService = cy_kit.singleton(
                     cy_xdoc.services.accounts.AccountService),
                 service_sercutity: cy_xdoc.services.secutities.Sercurity = cy_kit.singleton(
                     cy_xdoc.services.secutities.Sercurity)

                 ):
        self.service_search = service_search
        self.service_file = service_file
        self.service_app = service_app
        self.services_msg = services_msg
        self.service_storage = service_storage
        self.service_account = service_account
        self.service_sercutity = service_sercutity
        self.data_context = data_context


container: Container = cy_kit.singleton(Container)
"""
Khoi tao container
"""

DATA_ERROR_DUPLICATE = "duplicate"
ERROR_UNKNOWN = "unknown"


def get_error_code(ex):
    if isinstance(ex, pymongo.errors.DuplicateKeyError):
        return DATA_ERROR_DUPLICATE
    return ERROR_UNKNOWN


def get_error_fields(ex):
    if isinstance(ex, pymongo.errors.DuplicateKeyError):
        if hasattr(ex,'details') and isinstance(ex.details,dict) and isinstance(ex.details.get("keyPattern"),dict):
            return list(ex.details["keyPattern"].keys())
    return []


def get_error_message(ex):
    if isinstance(ex, pymongo.errors.DuplicateKeyError):
        return "Data value is existing"
    return "Unknown error"
