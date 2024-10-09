from cyx.common.base import config
from pymongo.mongo_client import MongoClient
from cyx.common.mongo_db_services import __create_client__ as __common_create_client__
from cyx.repository import Repository
import cy_docs
__client__ = {}

import urllib

from typing import Generic,TypeVar
T = TypeVar("T")
__cache_context__ = {}
__tenant_db__= None
__available_tenants__ = None
def get_available_tenants():
    global __available_tenants__
    return __available_tenants__
class TenantNotFound(Exception):
    def __init__(self, message,tenant_name):
        super().__init__(message)
        self.message = message
        self.tenant_name = tenant_name
    def __repr__(self):
        return f"message={self.message},tenant={self.tenant_name}"
def __create_client__(db) -> MongoClient:
    global __tenant_db__
    if isinstance(db, str):
        if __client__.get(db) is None:
            try:
                url_connection = urllib.parse.unquote(db)
                __client__[db] = MongoClient(url_connection)
            except:
                __client__[db] = MongoClient(db)

        return __client__[db]
    else:
        if __client__.get(db.host) is None:
            __client__[db.host] = MongoClient(**db.to_dict())
        return __client__[db.host]
class CodxRepositoryContext(Generic[T]):
    def __init__(self, cls: T):
        if config.get("db_codx") is None:
            self.__client__ = __common_create_client__(config.db)
        else:
            db = config.get("db_codx")
            self.__client__ = __create_client__(db)
        global __tenant_db__
        global __available_tenants__
        if __tenant_db__ is None:
            __tenant_db__ = set([x for x in self.__client__.list_database_names()])
            lv_file_tenant_agg = Repository.apps.app("admin").context.aggregate().project(
                cy_docs.fields.app_name >> Repository.apps.fields.Name
            )
            app_items = list(lv_file_tenant_agg)
            __tenant_db_in_lv_files__ = set([f"{x.app_name}_Data" for x in app_items if x.app_name not in  ["qtscdemo","hps-file-test"]])
            __tenant_db__ = __tenant_db__ & __tenant_db_in_lv_files__
            __available_tenants__ = [x[0:-len("_Data")] for x in __tenant_db__]


        self.__cls__ = cls
        self.__cache__ = {}
        self.__fields__ = cy_docs.cy_docs_x.fields[self.__cls__]

    @property
    def fields(self) -> T:
        return self.__fields__
    def tenant(self, tenant_name: str) -> cy_docs.DbQueryableCollection[T]:
        """
        Switch to tenant
        Exception: TenantNotFound
        @param app_name:
        @return:
        """

        if self.__cache__.get(tenant_name):
            return self.__cache__.get(tenant_name)
        else:
            db_name =f"{tenant_name}_Data"
            if db_name not in __tenant_db__:
                raise TenantNotFound(message="Tenant was not found",tenant_name=tenant_name)
            # if app_name == "admin":
            #     db_name = config.admin_db_name
            ret = cy_docs.DbQueryableCollection[T](self.__cls__, self.__client__, db_name)
            self.__cache__[tenant_name] = ret
            return ret
from cy_jobs.jobs.codx.models import (
    Codx_DM_FileInfo,
    Codx_WP_Comments
)
class CodxRepository:
    dm_file_info = CodxRepositoryContext[Codx_DM_FileInfo](Codx_DM_FileInfo)
    wp_comments = CodxRepositoryContext[Codx_WP_Comments](Codx_WP_Comments)
def main():
    data_item = CodxRepository.dm_file_info.app("thaone23").context.find_one({})
    print(data_item)
if __name__ == "__main__":
    main()

