import json
import pathlib
import sys
import os

import gunicorn.app.wsgiapp

WORKING_DIR = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append(os.path.join(pathlib.Path(__file__).parent.parent.__str__(), "cy_core"))
import cyx.common
from cyx.common import config

import fastapi
import datetime
import cy_kit
# from cyx.vn_predictor import VnPredictor
# vn_pre = cy_kit.singleton(VnPredictor)
# txt_non_accent = "Kiem tra he thong Tieng Viet khong dau"
# txt_accent  = vn_pre.get_text(txt_non_accent)
# print(txt_non_accent)
# print(txt_accent)
import cy_web
from cyx.common.msg import MessageService
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cyx.common

config = cyx.common.config
if isinstance(config.get('rabbitmq'), dict):
    cy_kit.config_provider(
        from_class=Broker,
        implement_class=RabitmqMsg
    )
from cyx.loggers import LoggerService

logger = cy_kit.singleton(LoggerService)
print(config)
from  cyx.vn_predictor import VnPredictor
vn_predictor= cy_kit.singleton(VnPredictor)
fx=vn_predictor.get_text("Kiem tra tieng viet khong dau")
print(fx)
from cyx.common.base import DbConnect

cnn = cy_kit.singleton(DbConnect)
cnn.set_tracking(True)
cy_app_web = cy_web.create_web_app(
    working_dir=WORKING_DIR,
    static_dir=config.static_dir, #os.path.abspath(os.path.join(WORKING_DIR, config.static_dir)),
    template_dir=config.jinja_templates_dir, #os.path.abspath(os.path.join(WORKING_DIR, config.jinja_templates_dir)),
    host_url=config.host_url,
    bind=config.bind,
    cache_folder="./cache",
    dev_mode=cyx.common.config.debug,

)


cy_web.add_cors(["*"])
from starlette.concurrency import iterate_in_threadpool


@cy_web.middleware()
async def codx_integrate(request: fastapi.Request, next):
    res = await next(request)
    return res


@cy_web.middleware()
async def estimate_time(request: fastapi.Request, next):
    try:
        start_time = datetime.datetime.utcnow()
        res = await next(request)
        n = datetime.datetime.utcnow()-start_time
        logger.info(f"{request.url}  in {n}")
        if request.url._url == cy_web.get_host_url() + "/api/accounts/token":
            response_body = [chunk async for chunk in res.body_iterator]
            res.body_iterator = iterate_in_threadpool(iter(response_body))
            if len(response_body) > 0:
                BODY_CONTENT = response_body[0].decode()

                try:
                    data = json.loads(BODY_CONTENT)
                    if data.get('access_token'):
                        res.set_cookie('access_token_cookie', data.get('access_token'))
                except Exception as e:
                    pass

        end_time = datetime.datetime.utcnow()
        async def apply_time(res):
            res.headers["time:start"] = start_time.strftime("%H:%M:%S")
            res.headers["time:end"] = end_time.strftime("%H:%M:%S")
            res.headers["time:total(second)"] = (end_time - start_time).total_seconds().__str__()
            res.headers["Server-Timing"] = f"total;dur={(end_time - start_time).total_seconds() * 1000}"
            return res
        res = await apply_time(res)
    except Exception as e:
        logger.error(e)
        raise e

    """HTTP/1.1 200 OK

Server-Timing: miss, db;dur=53, app;dur=47.2"""
    return res


cy_web.load_controller_from_dir("api", "./cy_xdoc/controllers")
app = cy_web.get_fastapi_app()
from cy_controllers import PagesController
from cy_controllers.apps.app_controller import AppsController
from cy_controllers.logs.logs_controller import LogsController
from cy_controllers.files.files_controller import FilesController
from cyx.loggers import LoggerService
logger_service = cy_kit.singleton(LoggerService)
app.include_router(
    prefix=cy_web.get_host_dir(),
    router=PagesController.router()
)
app.include_router(
    prefix=cy_web.get_host_dir(),
    router=AppsController.router()
)
app.include_router(
    prefix=cy_web.get_host_dir(),
    router=LogsController.router()
)
app.include_router(
    router=  FilesController.router(),
    prefix=cy_web.get_host_dir(),
)
import multiprocessing
def get_number_of_cpus():
  # Get the number of logical CPUs
  logical_cpus = os.cpu_count()

  # Get the number of physical CPUs (excluding hyperthreading)
  physical_cpus = multiprocessing.cpu_count()

  return logical_cpus, physical_cpus

from gunicorn.app.wsgiapp import (
    WSGIApplication,
    run,util, Application

)
from gunicorn.app.base import BaseApplication
from typing import (
    Callable,Dict,Any
)
class StandaloneApplication(BaseApplication):
    def __init__(self, application: Callable, options: Dict[str, Any] = None):
        self.options = options or {}
        self.application = application
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
number_of_workers = get_number_of_cpus()[0]
if config.workers!="auto":
    if isinstance(config.workers,int):
        number_of_workers = config.workers
    else:
        number_of_workers = 1
if __name__ == "__main__":
    options = {
        "bind": "%s:%s" % (cy_app_web.bind_ip, cy_app_web.bind_port),
        "workers": number_of_workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "timeout_keep_alive":30,
        "timeout_graceful_shutdown":10
    }
    print(options)
    StandaloneApplication(app, options).run()
# if __name__ == "__main__":

    # application = WSGIApplication(cy_web.get_fastapi_app())
    # number_of_workers = get_number_of_cpus()[0]
    # number_of_workers = 1
    # logger_service.info(f"Strat web app worker={number_of_workers}")

    import gunicorn
    from gunicorn import SERVER



    # cy_web.start_with_uvicorn(worker=number_of_workers)
    # cy_web.start_with_guicorn(worker=number_of_workers)
    # from gunicorn.app import wsgiapp
    #
    #
    # wsgiapp.run()
    ""