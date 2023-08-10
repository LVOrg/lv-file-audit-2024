"""
Đễ chạy được FastAPI ở chế độ deploy ra intrenet
iis sẽ dùng Fastcgi để start file này
"""
import sys
import pathlib

import enig_frames.containers
import fasty
import os
fasty.load_config(os.environ["PYTHONPATH"],"uvicorn.error")
import fasty.JWT
fasty.JWT.set_default_db(fasty.config.db.authSource)
import api_app
from a2wsgi import ASGIMiddleware
enig_frames.containers.Container.loggers.get_logger(__name__).info(
"Web api run on iis start"
)




wsgi_app = ASGIMiddleware(api_app.app)
