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


class MongodbService:
    def __init__(self):
        self.admin_db_name = config.admin_db_name
        self.client = __create_client__(config.db)

    def db(self, db_name: str) -> cy_docs.DbQueryable:
        if db_name == "admin":
            ret = cy_docs.DbQueryable(self.admin_db_name, self.client)
            return ret
        else:
            ret = cy_docs.DbQueryable(db_name, self.client)
            return ret
