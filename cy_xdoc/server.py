import gc
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

# if config.debug == False:
# from  cyx.vn_predictor import VnPredictor
# vn_predictor= cy_kit.singleton(VnPredictor)
# fx=vn_predictor.get_text("Kiem tra tieng viet khong dau hello")
# print(fx)
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
            # res.headers["time:start"] = start_time.strftime("%H:%M:%S")
            # res.headers["time:end"] = end_time.strftime("%H:%M:%S")
            # res.headers["time:total(second)"] = (end_time - start_time).total_seconds().__str__()
            res.headers["Server-Timing"] = f"total;dur={(end_time - start_time).total_seconds() * 1000}"
            return res
        res = await apply_time(res)
    except Exception as e:
        logger.error(e)
        raise e

    """HTTP/1.1 200 OK

Server-Timing: miss, db;dur=53, app;dur=47.2"""
    gc.collect()
    return res


cy_web.load_controller_from_dir("api", "./cy_xdoc/controllers")
app = cy_web.get_fastapi_app()
from cy_xdoc.load_controllers import load_controller
load_controller(
    app,
    cy_web.get_host_dir()
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
from cyx.cache_service.memcache_service import MemcacheServices
# cache_service = cy_kit.singleton(MemcacheServices)
# cache_service.check_connection(timeout=60*60*2)
if config.worker_class:
    worker_class =f"uvicorn.workers.{config.worker_class}"
else:
    worker_class = "uvicorn.workers.UvicornWorker"
timeout_keep_alive=30
timeout_graceful_shutdown = 30
if config.timeout_keep_alive:
    timeout_keep_alive = config.timeout_keep_alive
if config.timeout_graceful_shutdown:
    timeout_keep_alive = config.timeout_graceful_shutdown

# if __name__ =="__main__":

if __name__ == "__main__":
    if config.server_type == "unvicorn":
        options = {
            "bind": "%s:%s" % (cy_app_web.bind_ip, cy_app_web.bind_port),
            "workers": number_of_workers,
            "worker_class": worker_class,
            "timeout_keep_alive":30,
            "timeout_graceful_shutdown":10
        }
        print(options)
        StandaloneApplication(app, options).run()
    elif config.server_type == "hypercorn":
        import hypercorn.config, hypercorn.run

        _config_ = hypercorn.config.Config()
        _config_.bind = [f"{cy_app_web.bind_ip}:{cy_app_web.bind_port}"]
        _config_.application_path = "cy_web:get_fastapi_app()"
        _config_.workers = number_of_workers
        _config_.keep_alive_timeout = config.timeout_keep_alive
        # _config_.h2_max_concurrent_streams = 100
        _config_.worker_class = config.worker_class
        print(_config_.__dict__)
        hypercorn.run.run(_config_)
    else:
        cy_web.start_with_uvicorn(worker=number_of_workers)
# if __name__ == "__main__":
#
#
#     logger_service.info(f"Strat web app worker={number_of_workers}")

    import gunicorn
    from gunicorn import SERVER



    # cy_web.start_with_uvicorn(worker=number_of_workers)

    # from gunicorn.app import wsgiapp
    #
    #
    # wsgiapp.run()
    ""