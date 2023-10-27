import json
import os
import pathlib
import logging
import traceback
import datetime
import cy_docs
import typing


@cy_docs.define(
    name="SYS_AdminLoggers",
    indexes=[
        "CreatedOn", "LogType","PodName","PodFullName"
    ]
)
class sys_app_logs:
    CreatedOn: datetime.datetime
    Content: str
    LogType: str
    PodFullName: typing.Optional[str]
    PodName: typing.Optional[str]


"""
The main class in this package is FileServices. FileServices supports fully access to DocUploadRegister Collection
"""
import datetime
import os.path
import pathlib
import threading
import cy_kit
import cyx.common.file_storage
import cyx.common.base
import cyx.common.cacher
import traceback
import slack.webhook
from cyx.common import config

class LoggerService:
    def __init__(self, db_connect=cy_kit.inject(cyx.common.base.DbConnect)):



        self.full_pod_name = None
        self.pod_name = None
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
        if hasattr(config,"logs_url"):
            self.slack_client = slack.webhook.WebhookClient(config.logs_url)
            __fulll_pod_name = self.get_fullname_of_pod()
            try:
                slack_data = self.get_info_for_slack(f'Start logs from {self.get_fullname_of_pod()}')
                self.slack_client.send(text=slack_data)

            except Exception as e:
                content = traceback.format_exc()
                try:
                    self.slack_client.send(text=content)
                except Exception as e:
                    print(content)
                    self.slack_client=None
        # Log a message

    def get_mongo_db(self) -> cyx.common.base.DbCollection[sys_app_logs]:
        doc = self.db_connect.db("admin").doc(sys_app_logs)
        return doc

    def info(self, txt):
        try:
            if isinstance(txt,dict):
                txt = json.dumps(txt,indent=1)
            now = datetime.datetime.utcnow()
            print(f'[INFO][{now.strftime("%Y%m/%d/ %H:%M:%S")}][{self.get_fullname_of_pod()}]: {txt}')
            self.__logger__.info(txt)
            self.write_to_mongodb(created_on=now, log_type="info", content=txt)
        except Exception as ex:
            self.__logger__.error(ex)

    def get_fullname_of_pod(self):
        if self.full_pod_name is None:
            f = open('/etc/hostname')
            pod_name = f.read()
            f.close()
            self.full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        return self.full_pod_name

    def get_name_of_pod(self):
        if self.pod_name is None:
            full_name = self.get_fullname_of_pod()
            items = full_name.split('-')
            if len(items)>2:
                self.pod_name = "-".join(items[:-2])
            else:
                self.pod_name = full_name
        return self.pod_name

    def error(self, ex,more_info=None):
        try:
            if isinstance(more_info,dict):
                more_info = json.dumps(more_info,indent=1)
            now = datetime.datetime.utcnow()
            content = traceback.format_exc()
            content =f"{more_info}/n/n-----------------{content}"
            print(f'[ERROR][{now.strftime("%Y%m/%d/ %H:%M:%S")}][{self.get_fullname_of_pod()}]: {content}')

            self.__logger__.exception("An exception occurred: %s", ex, exc_info=True)
            if self.slack_client is None:
                self.write_to_mongodb(created_on=now, log_type="error", content=content)
            else:
                slack_data= self.get_info_for_slack(traceback.format_exc(),more_info=more_info)

                self.slack_client.send(text=content,attachments=[slack_data])
        except Exception as ex:
            self.__logger__.error(ex)

    def write_to_mongodb(self, created_on, log_type, content):
        def running():
            try:
                context = self.get_mongo_db().context
                fields = self.get_mongo_db().fields
                context.insert_one(
                    fields.LogType << log_type,
                    fields.CreatedOn << created_on,
                    fields.Content << content,
                    fields.PodFullName << self.get_fullname_of_pod(),
                    fields.PodName << self.get_name_of_pod()
                )
            except Exception as e:
                print(traceback.format_exc())

        threading.Thread(target=running, args=()).start()

    def get_info_for_slack(self,content:str,more_info:dict=None)->str:
        ret = dict(
            pod=self.get_fullname_of_pod(),
            name=self.get_name_of_pod(),
            time=datetime.datetime.utcnow().strftime("%d/%m/%Y:%H:%M:%S"),
            content = content
        )
        if isinstance(more_info,dict):
            ret["more_info"]=more_info
        json_string = json.dumps(ret, indent=4)
        return json_string
