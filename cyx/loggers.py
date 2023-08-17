import os
import pathlib
import logging


class LoggerService:
    def __init__(self):
        self.__working_dir__ = pathlib.Path(__file__).parent.parent.__str__()
        self.__log_dir__ = os.path.abspath(
            os.path.join(self.__working_dir__, "share-storage", "logger")
        )
        self.__log_path__ = os.path.abspath(
            os.path.join(self.__log_dir__, "logs.log")
        )
        if not os.path.isdir(self.__log_dir__):
            os.makedirs(self.__log_dir__,exist_ok=True)
        self.__logger__ = logginglogging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.INFO,
            filename=self.__log_path__,
            filemode="w",
        )

    def info(self, txt):
        self.__logger__.info(txt)
