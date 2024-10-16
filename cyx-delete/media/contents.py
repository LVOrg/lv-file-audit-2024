import os
import pathlib
import sys
import typing

from cyx.common import config
class ContentsServices:
    def __init__(self):
        self.config = config
        self.working_path = str(pathlib.Path(__file__).parent)
        self.ext_lib_folder = os.path.join(str(pathlib.Path(__file__).parent), "../ext_libs")
        # path_to_java = os.path.join(self.ext_lib_folder, "tika-server.jar")
        # path_to_java_md5 = os.path.join(self.ext_lib_folder, "tika-server.jar.md5")
        # if not os.path.isfile(path_to_java):
        #     raise Exception(f"f{path_to_java} was not found")
        # if not os.path.isfile(path_to_java_md5):
        #     raise Exception(f"f{path_to_java_md5} was not found")
        # os.environ['TIKA_SERVER_JAR'] = path_to_java
        # os.environ['TIKA_PATH'] = self.ext_lib_folder
        # os.environ['TIKA_STARTUP_SLEEP'] = '10'
        # os.environ['TIKA_STARTUP_MAX_RETRY'] = '10'
        # if sys.modules.get("tika") is not None:
        #     import importlib
        #     importlib.reload(sys.modules["tika"])
    def get_text(self, file_path) -> typing.Tuple[str, dict]:
        """
        With Giga bytes file pdf, or other office file, need split to small doc with 100 pages oer doc
        :param file_path:
        :return:
        """

        import tika

        from tika import parser

        headers = {
            'maxWriteLimit': '2147483647'
        }
        ret = parser.from_file(
            filename=file_path,
            serverEndpoint=f'http://localhost:9998/tika',
            requestOptions={'headers': headers, 'timeout': 30000}
        )

        # ret = parser.from_file(file_path,  requestOptions={'headers': headers, 'timeout': 30000})
        # import psutil
        # import signal
        # for x in psutil.process_iter():
        #     if x.status() == 'sleeping' and x.__name__() == 'java':
        #         os.kill(x.pid, signal.SIGKILL)
        return ret['content'], ret['metadata']