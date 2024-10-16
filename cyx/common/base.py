import datetime
import threading
import typing

import pymongo.database

import cy_docs
import cy_kit
from cyx.common import config

from pymongo.mongo_client import MongoClient
from typing import TypeVar, Generic
import urllib

T = TypeVar("T")

__client__ = {}


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


class DbCollection(Generic[T]):
    def __init__(self, cls, client: MongoClient, db_name: str):
        self.__cls__ = cls
        self.__client__ = client
        self.__db_name__ = db_name

    @property
    def context(self):
        """
        Query context full Mongodb Access
        :return:
        """
        ret = cy_docs.context(
            client=self.__client__,
            cls=self.__cls__
        )[self.__db_name__]
        return ret

    @property
    def fields(self) -> T:
        return cy_docs.expr(self.__cls__)


class DB:
    def __init__(self, client: MongoClient, db_name: str):
        self.__client__ = client
        self.__db_name__ = db_name

    def doc(self, cls: T) -> DbCollection[T]:
        return DbCollection[T](cls, self.__client__, self.__db_name__)


class DbConnect:
    def __init__(self):
        self.connect_config = config.db
        self.admin_db_name = config.admin_db_name
        self.client = __create_client__(config.db)
        self.__tracking__ = False
        print("load connect is ok")

    def db(self, app_name):
        db_name = app_name
        if app_name == 'admin':
            db_name = self.admin_db_name
        else:
            self.do_tracking(app_name)
        return DB(client=self.client, db_name=db_name)

    def set_tracking(self, is_tracking):
        self.__tracking__ = is_tracking

    def do_tracking(self, app_name):
        def run():
            # from cy_xdoc.models.apps import App
            from cyx.repository import Repository
            db = DB(client=self.client, db_name=self.admin_db_name)
            db_stats = dict()
            try:
                db_stats = db.__client__.get_database(app_name).command("dbStats")
                print(db_stats.get("storageSize"))
            except:
                pass
            db_context = Repository.apps.app("admin")
            storage_size = db_stats.get("storageSize",0)
            db_context.context.update(
                db_context.fields.Name == app_name,
                db_context.fields.SizeInGB<<storage_size/(1024**3),
                {
                    "$inc": {
                        "AccessCount": 1
                    },
                    "LatestAccess": datetime.datetime.utcnow()
                }
            )
        if self.__tracking__:
            threading.Thread(target=run,args=()).start()


class __DbContext__:
    def __init__(self, db_name: str, client: MongoClient):
        self.client = client
        self.db_name = db_name

    def doc(self, cls: T):
        return cy_docs.context(
            client=self.client,
            cls=cls

        )[self.db_name]


class DbClient:
    def __init__(self):
        global __client__
        self.config = config
        self.client = __create_client__(config.db)

        print("Create connection")


class Base:
    def __init__(self, db_client: DbClient = cy_kit.single(DbClient)):

        self.config = db_client.config
        self.client = db_client.client

    def expr(self, cls: T) -> T:
        return cy_docs.expr(cls)

    def db_name(self, app_name: str):
        if app_name == 'admin':
            return config.admin_db_name
        else:
            return app_name

    def db(self, app_name: str):
        return __DbContext__(self.db_name(app_name), self.client)

    async def get_file_async(self, app_name: str, file_id):
        return await cy_docs.get_file_async(self.client, self.db_name(app_name), file_id)
