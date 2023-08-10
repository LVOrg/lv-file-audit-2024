"""
Đây là file  app để chạy api
Với môi trường dev hoặc chạy test
dùng windows command line
Chạy uvicorn api_app:app --reload
"""



import os
import sys
import pathlib
for x in sys.argv:
    print(x)
import uvicorn.server
import fasty
import uvicorn
print("-----port--------------")
print(os.getenv('file_server_bind_port'))
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))







import fasty
import pathlib
app = fasty.install_fastapi_app(__name__)


import fasty_api
"""
Napapi
"""
import fasty_pages
"""
Nap trang quan ly
"""
import enig_frames.containers
enig_frames.containers.Container.loggers.get_logger(__name__).info(
    f" start app {__name__} in {__file__}"
)

# fasty.logger.logger.info("start in iis")

#uvicorn api_app:app --reload