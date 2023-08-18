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

    def info(self, txt):
        self.__logger__.info(txt)

    def error(self, ex):
        self.__logger__.exception("An exception occurred: %s", ex, exc_info=True)
