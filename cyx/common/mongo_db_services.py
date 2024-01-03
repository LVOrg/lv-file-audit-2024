from cyx.common.base import config
from pymongo.mongo_client import MongoClient
import cy_docs

__client__ = {}

import urllib


def __create_client__(db) -> MongoClient:
    if isinstance(db, str):
        if __client__.get(db) is None:
            url_connection = urllib.parse.unquote(config.db)
            # if "connectTimeoutMS=" not in url_connection:
            #     if "/?" in url_connection:
            #         url_connection += "&connectTimeoutMS=15000&socketTimeoutMS=15000"
            #     else:
            #         url_connection += "/?connectTimeoutMS=15000&socketTimeoutMS=15000"
            __client__[db] = MongoClient(url_connection)

        return __client__[db]
    else:
        if __client__.get(db.host) is None:
            __client__[db.host] = MongoClient(**db.to_dict())
        return __client__[db.host]

from typing import TypeVar, Generic
T = TypeVar("T")
__cache_context__ = {}
class DbDocumentContext(Generic[T]):
    def __init__(self,doc_type:T):
        self.doc_type = doc_type

class DbContext:
    def __init__(self,client,db_name:str):
        self.client=client
        self.db_name = db_name
    def doc(self,cls:T)->DbDocumentContext[T]:
        if __cache_context__.get(self.db_name):
            return __cache_context__[self.db_name]
        ret = cy_docs.DbQueryable(self.db_name, self.client)
        __cache_context__[self.db_name] = ret
        return ret



class MongodbService:
    def __init__(self):
        self.admin_db_name = config.admin_db_name
        self.client = __create_client__(config.db)
        self.__context__ =  {}

    def db(self, db_name: str) -> cy_docs.DbQueryable:
        if db_name == "admin":
            ret = cy_docs.DbQueryable(self.admin_db_name, self.client)
            return ret
        else:
            ret = cy_docs.DbQueryable(db_name, self.client)
            return ret

    def get_db_context(self,db_name:str)->DbContext:
        if db_name == "admin":
            if self.__context__.get(self.admin_db_name):
                return self.__context__.get(self.admin_db_name)
            ret = DbContext(self.client,self.admin_db_name)
            self.__context__[self.admin_db_name] = ret
            return ret
        else:
            if self.__context__.get(db_name):
                return self.__context__.get(db_name)
            ret = DbContext(self.client, db_name)
            self.__context__[db_name] = ret
            return ret