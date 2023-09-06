import os
import pathlib
import logging


class Logger:
    def __init__(self):
        self.__working_dir__ = pathlib.Path(__file__).parent.parent.__str__()
        self.__log_path__ = os.path.abspath(
            os.path.join(self.__working_dir__, "share-storage", "logger", "logs.log")
        )
        self.__logger__ = logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.INFO,
            filename=self.__log_path__,
            filemode="w",
        )
