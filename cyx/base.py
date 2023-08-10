import logging
import pathlib
import os
import cy_kit


class Config:
    def __init__(self):
        self.working_folder = pathlib.Path(__file__).parent.parent.__str__()

    def load(self, yaml_config_path):
        self.config_path = yaml_config_path
        if self.config_path[0:2] == "./":
            self.config_path = os.path.abspath(os.path.join(
                self.working_folder,
                self.config_path[2:].replace('/', os.sep)
            ))
        self.config_data = cy_kit.yaml_config(self.config_path)

    def __getattr__(self, item):
        return getattr(self.config_data, item)


class Base:
    def __init__(
            self,
            config: Config = cy_kit.singleton(Config)):
        self.config = config
        self.working_folder = config.working_folder
        self.host_ip = cy_kit.get_local_host_ip()
        self.logs: logging.Logger = None

    def init(self, name):
        self.logs = cy_kit.create_logs(
            os.path.join(self.working_folder, "logs"), name)
        self.processing_folder = self.config.tmp_media_processing_folder
        if self.processing_folder[0:2] == "./":
            self.processing_folder = self.processing_folder[2:]
            self.processing_folder = os.path.abspath(
                os.path.join(self.working_folder, self.processing_folder.replace('/', os.sep)))
        self.processing_folder = os.path.join(self.processing_folder, name)
        self.processing_folder = self.processing_folder.replace('/', os.sep)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)

    def get_file_extenstion(self, file_path) -> str:
        return os.path.splitext(file_path)[1][1:]

    def get_file_name_only(self, file_path) -> str:
        return pathlib.Path(file_path).stem


import pymongo.database

import cy_docs
import cy_kit

from cy_docs import get_doc
from pymongo.mongo_client import MongoClient
from typing import TypeVar, Generic

T = TypeVar("T")

config = cy_kit.yaml_config(os.path.join(
    pathlib.Path(__file__).parent.parent.__str__(), "config.yml"
))
config_path = os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(), "config.yml")


class DbCollection(Generic[T]):
    def __init__(self, cls, client: MongoClient, db_name: str):
        self.__cls__ = cls
        self.__client__ = client
        self.__db_name__ = db_name

    @property
    def context(self):
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
        self.client = MongoClient(**self.connect_config.to_dict())
        print("load connect is ok")

    def db(self, app_name):
        db_name = app_name
        if app_name == 'admin':
            db_name = self.admin_db_name
        return DB(client=self.client, db_name=db_name)


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
        self.config = config
        self.client = MongoClient(**config.db.to_dict())
        print("Create connection")


class BaseService:
    def __init__(self, db_connect: DbConnect = cy_kit.singleton(DbConnect)):
        self.db_connect: DbConnect = db_connect

    def db_name(self, app_name: str):
        if app_name == 'admin':
            return config.admin_db_name
        else:
            return app_name

    def db(self, app_name: str):
        return __DbContext__(self.db_name(app_name), self.client)
