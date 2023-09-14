import os
import pathlib
import logging
import traceback
import datetime
import cy_docs
@cy_docs.define(
    name="SYS_AdminLogs",
    indexes=[
        "CreatedOn","LogType"
    ]
                )
class sys_app_logs:
    CreatedOn: datetime.datetime
    Content: str
    LogType:str


"""
The main class in this package is FileServices. FileServices supports fully access to DocUploadRegister Collection
"""
import datetime
import mimetypes
import os.path
import pathlib
import threading
import time
import typing
import uuid

import bson
import humanize
import cy_docs
import cy_kit
import cy_web
import cyx.common.file_storage
import cyx.common.base
import cyx.common.cacher
import traceback

class LoggerService:
    def __init__(self,db_connect=cy_kit.inject(cyx.common.base.DbConnect)):
        self.db_connect = db_connect
        self.__working_dir__ = pathlib.Path(__file__).parent.parent.__str__()
        self.__log_dir__ = os.path.abspath(
            os.path.join(self.__working_dir__, "share-storage", "logger")
        )
        self.__log_path__ = os.path.abspath(
            os.path.join(self.__log_dir__, "logs.log")
        )
        if not os.path.isdir(self.__log_dir__):
            os.makedirs(self.__log_dir__, exist_ok=True)
        self.__logger__ = logging.getLogger("centralize")

        # Set the logging level to DEBUG
        self.__logger__.setLevel(logging.DEBUG)

        # Create a file handler and set the file path
        file_handler = logging.FileHandler(self.__log_path__)

        # Set the format for the log messages
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.__logger__.addHandler(file_handler)

        # Log a message
    def get_mongo_db(self)->cyx.common.base.DbCollection[sys_app_logs]:
        doc = self.db_connect.db("admin").doc(sys_app_logs)
        return doc
    def info(self, txt):
        try:
            now = datetime.datetime.now()
            print(f'[INFO][{now.strftime("%m/%d/%Y %H:%M:%S")}]: {txt}')
            self.__logger__.info(txt)
            self.write_to_mongdb(created_on=now, log_type="info", content=txt)
        except:
            pass

    def error(self, ex):
        now = datetime.datetime.now()
        content = traceback.format_exc()
        print(f'[ERROR][{now.strftime("%m/%d/%Y %H:%M:%S")}]: {content}')

        self.__logger__.exception("An exception occurred: %s", ex, exc_info=True)
        self.write_to_mongdb(created_on=now, log_type="error", content=content)

    def write_to_mongdb(self, created_on, log_type, content):
        def running():
            try:
                context = self.get_mongo_db().context
                fields = self.get_mongo_db().fields
                context.insert_one(
                    fields.LogType <<log_type,
                    fields.CreatedOn << created_on,
                    fields.Content << content
                )
            except Exception as e:
                print(traceback.format_exc())
        threading.Thread(target=running,args=()).start()

