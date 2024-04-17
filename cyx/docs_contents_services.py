import time




import requests


class DocsContentsServices:
    def __init__(self):
        ok = False
        while not ok:
            try:
                response = requests.get("http://localhost:9998/tika")
                response.raise_for_status()
                ok = True
            except:
                print(f"try connect to http://localhost:9998/tika")
                time.sleep(5)

    def get_text(self, file_path: str):
        import tika.parser
        headers = {
            'maxWriteLimit': '2147483647'
        }
        ret = tika.parser.from_file(
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
        if isinstance(ret, dict):
            return ret.get('content')
        else:
            return ""
