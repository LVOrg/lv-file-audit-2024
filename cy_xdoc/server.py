import functools
import gc
import json
import pathlib
import sys
import os
import traceback

WORKING_DIR = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

print(os.getenv("DB__CNN"))
sys.path.append("/app")
import cy_kit
from cyx.file_utils_services import FileUtilService
file_util_service=cy_kit.singleton(FileUtilService)

from cyx.runtime_config_services import RuntimeConfigService

runtime_config_service = cy_kit.singleton(RuntimeConfigService)
runtime_config_service.load(sys.argv)
skip_checking = os.getenv("BUILD_IMAGE_TAG") is None

import cyx.framewwork_configs

import cyx.common
from cyx.common import config
version2 = config.generation if hasattr(config,"generation") else None
file_util_service.healthz() if version2 else print("Run firs generation")

# if not skip_checking or (hasattr(config,"check_startup") and config.check_startup):
#import cyx.check_start_up
# if hasattr(config,"file_storage_encrypt") and config.file_storage_encrypt==True:
import cy_file_cryptor.wrappers
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Set to None to disable the limit (not recommended)

import cy_file_cryptor.context

cy_file_cryptor.context.set_server_cache(config.cache_server)
import cy_file_cryptor.settings

cy_file_cryptor.settings.set_encrypt_folder_path(config.file_storage_path)

import fastapi
import datetime

import cy_web
from cyx.common.msg import MessageService
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cyx.common
from fastapi.middleware.gzip import GZipMiddleware

config = cyx.common.config
from cyx.distribute_locking.distribute_lock_services import DistributeLockService

# distribute_lock_service = cy_kit.singleton(DistributeLockService)

if isinstance(config.get('rabbitmq'), dict):
    cy_kit.config_provider(
        from_class=Broker,
        implement_class=RabitmqMsg
    )
from cyx.loggers import LoggerService

logger = cy_kit.singleton(LoggerService)
import cy_kit.config_utils

config_list = cy_kit.config_utils.flatten_dict(config)
for k, v in config_list:
    print(f"{k}={v}")

if hasattr(config, "auto_ssl_redirect") and config.auto_ssl_redirect == "on":
    if not config.host_url.startswith("https://"):
        config.host_url = "https://" + config.host_url[len("http://"):]

from cyx.common.base import DbConnect
cnn = cy_kit.singleton(DbConnect)

cnn.set_tracking(True)
config.server_type="Uvicorn"
config.worker_class="httptools"
cy_app_web = cy_web.create_web_app(
    working_dir=WORKING_DIR,
    static_dir=config.static_dir,  #os.path.abspath(os.path.join(WORKING_DIR, config.static_dir)),
    template_dir=config.jinja_templates_dir,  #os.path.abspath(os.path.join(WORKING_DIR, config.jinja_templates_dir)),
    host_url=config.host_url,
    bind=config.bind,
    cache_folder="./cache",
    dev_mode=cyx.common.config.debug,

)
if hasattr(config, "auto_ssl_redirect") and config.auto_ssl_redirect == "on":
    print(f"Run app with https redirect automatically")
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

    cy_app_web.app.add_middleware(HTTPSRedirectMiddleware)
from fastapi import HTTPException

cy_web.add_cors(["*"])
from starlette.concurrency import iterate_in_threadpool

from cyx.repository import Repository

# Repository.sys_app_logs_coll.app("admin").context.delete(
#     {}
# )
@functools.cache
def get_pod_name():
    f = open('/etc/hostname')
    pod_name = f.read()
    f.close()
    full_pod_name = pod_name.lstrip('\n').rstrip('\n')
    items = full_pod_name.split('-')
    if len(items) > 2:
        pod_name = "-".join(items[:-2])
    else:
        pod_name = full_pod_name
    return pod_name
async def tracking_error_async(request: fastapi.Request):
    header = {}
    for k, v in request.headers.items():
        header[k] = v
    body_bytes = await request.body()
    form_data = await request.form()
    body_text = body_bytes.decode()  # Decod
    form_data_dict = {}
    for k,v in form_data.items():
        form_data_dict[k]=v
    data_content=json.dumps(dict(
        header=header,
        body_text=body_text,
        form=form_data_dict

    ),indent=4)
    ret = await Repository.sys_app_logs_coll.app("admin").context.insert_one_async(
        Repository.sys_app_logs_coll.fields.CreatedOn<<datetime.datetime.utcnow(),
        Repository.sys_app_logs_coll.fields.LogType<<"info",
        Repository.sys_app_logs_coll.fields.PodName<<get_pod_name(),
        Repository.sys_app_logs_coll.fields.Content<<data_content
    )
    if hasattr(ret,"inserted_id"):
        request.session["$$$inserted_id$$$"]=ret.inserted_id





# @cy_web.middleware()
# async def codx_integrate(request: fastapi.Request, next):
#     if request.url.path.endswith("/cloud/mail/send"):
#         await tracking_error_async(request)
#         print("OK")
#     res = await next(request)
#     return res


from fastapi.responses import JSONResponse
from cyx.malloc_services import MallocService
malloc_service=cy_kit.singleton(MallocService)
@cy_web.middleware()
async def estimate_time(request: fastapi.Request, next):
    try:
        start_time = datetime.datetime.utcnow()
        res = await next(request)
        n = datetime.datetime.utcnow() - start_time

        if not request.url.path.endswith("/api/healthz") and not request.url.path.endswith("/api/readyz"):
            logger.info(f"{request.url}  in {n}")
        if ((request.url._url == cy_web.get_host_url(request) + "/api/accounts/token")
                or (request.url._url == cy_web.get_host_url(request) + "/lvfile/api/accounts/token")):
            response_body = [chunk async for chunk in res.body_iterator]
            res.body_iterator = iterate_in_threadpool(iter(response_body))
            if len(response_body) > 0:
                BODY_CONTENT = response_body[0].decode()

                try:
                    data = json.loads(BODY_CONTENT)
                    del data
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
        #getattr(request,"log_mongoddb_track_id")
        res = await apply_time(res)

    except Exception as ex:
        print(traceback.format_exc())
        if request.session.get("$$$inserted_id$$$"):
            data_item= await Repository.sys_app_logs_coll.app("admin").context.find_one_async(
                Repository.sys_app_logs_coll.fields.id==request.session.get("$$$inserted_id$$$")
            )
            if data_item:
                data_content= json.loads(data_item[Repository.sys_app_logs_coll.fields.Content])
                data_content["Error"]=traceback.format_exc()
                data_content_text= json.dumps(data_content,indent=4)
                await Repository.sys_app_logs_coll.app("admin").context.update_async(
                    Repository.sys_app_logs_coll.fields.id == request.session.get("$$$inserted_id$$$"),
                    Repository.sys_app_logs_coll.fields.Content<<data_content_text
                )
            del request.session["$$$inserted_id$$$"]
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=traceback.format_exc(),
            status_code=500
        )
    except FileNotFoundError as e:
        image_tag: str = os.getenv("BUILD_IMAGE_TAG") or "-qc"
        if image_tag.endswith("-qc"):
            from fastapi.responses import HTMLResponse
            return HTMLResponse(
                content=traceback.format_exc(),
                status_code=500
            )
        else:
            # logger.error(e, more_info= dict(
            #     url= request.url.path
            # ))
            return JSONResponse(status_code=404, content={"detail": "Resource not found"})

    except Exception as e:
        logger.error(e, more_info=dict(
            url=request.url.path
        ))
        setattr(request,"lv_file_error_content",traceback.format_exc())
        return JSONResponse(status_code=500, content={"detail": "Server error"})

    finally:
        gc.collect()
        malloc_service.reduce_memory()
    return res


from fastapi import Request, Response

# from requests_kerberos import HTTPKerberosAuth
# import requests_kerberos.exceptions
# @cy_web.middleware()
# async def kerberos_auth_middleware(request: Request, call_next):
#     try:
#         auth = HTTPKerberosAuth()
#         response = await call_next(request)
#
#         return response
#     except requests_kerberos.exceptions.KerberosExchangeError as exc:
#         return Response(status_code=401, content=f"Authentication failed: {exc}")

# cy_web.load_controller_from_dir("api", "./cy_xdoc/controllers")
app = cy_web.get_fastapi_app()

from cyx.common.base import config
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key=config.jwt.secret_key)
GZipMiddleware(app)

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
    run, util, Application

)
from gunicorn.app.base import BaseApplication
from typing import (
    Callable, Dict, Any
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
if config.workers != "auto":
    if isinstance(config.workers, int):
        number_of_workers = config.workers
    else:
        number_of_workers = 1
from cyx.cache_service.memcache_service import MemcacheServices

# cache_service = cy_kit.singleton(MemcacheServices)
# cache_service.check_connection(timeout=60*60*2)
if config.worker_class:
    worker_class = f"uvicorn.workers.{config.worker_class}"
else:
    worker_class = "uvicorn.workers.UvicornWorker"
timeout_keep_alive = 30
timeout_graceful_shutdown = 30
if config.timeout_keep_alive:
    timeout_keep_alive = config.timeout_keep_alive
if config.timeout_graceful_shutdown:
    timeout_keep_alive = config.timeout_graceful_shutdown

# if __name__ =="__main__":
import multiprocessing
import subprocess
import signal
import resource
def run_fastapi_app(number_of_workers):
    """Runs the FastAPI application with limited memory in a background process.

    Args:
        number_of_workers (int): The desired number of Uvicorn workers.

    Raises:
        OSError: If memory limit cannot be set (Linux/macOS).
    """

    def start_app():
        # Implement logic to start the FastAPI application with cy_web.start_with_uvicorn
        cy_web.start_with_uvicorn(worker=number_of_workers)

    # Create a new process with limited memory (Linux/macOS)
    if hasattr(resource, 'RLIMIT_AS'):  # Check if resource module supports memory limit
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_AS)
        # Set a lower memory limit for the child process (adjust as needed)
        new_limit = soft_limit // 20  # Example: Set memory limit to half of the available memory
        try:
            resource.setrlimit(resource.RLIMIT_MEMLOCK, (50*1024**2, 50*1024**2))
        except OSError as e:
            print("Failed to set memory limit:", e)

    process = multiprocessing.Process(target=start_app)
    process.start()

    # Graceful termination (optional):
    def handle_signal(sig, frame):
        process.terminate()
        print("FastAPI application terminated (signal:", sig, ")")

    signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C interrupt
    signal.signal(signal.SIGTERM, handle_signal)  # Handle termination signals

    process.join()  # Wait for the child process to finish
config.server_type="uvicorn"
if __name__ == "__main__":
    if config.server_type.lower() == "uvicorn1":
        options = {
            "bind": "%s:%s" % (cy_app_web.bind_ip, cy_app_web.bind_port),
            "workers": number_of_workers,
            "worker_class": worker_class,
            "timeout_keep_alive": 30,
            "timeout_graceful_shutdown": 10
        }
        print(options)
        logger.info(json.dumps(options))
        StandaloneApplication(app, options).run()
    elif config.server_type == "hypercorn":
        import hypercorn.config, hypercorn.run

        _config_ = hypercorn.config.Config()
        _config_.bind = [f"{cy_app_web.bind_ip}:{cy_app_web.bind_port}"]
        _config_.application_path = "cy_web:get_fastapi_app()"
        _config_.workers = number_of_workers
        _config_.keep_alive_timeout = config.timeout_keep_alive
        if config.h2_max_concurrent_streams != "auto":
            _config_.h2_max_concurrent_streams = config.h2_max_concurrent_streams
        _config_.worker_class = config.worker_class
        if config.timeout_graceful_shutdown != "auto":
            _config_.shutdown_timeout = config.timeout_graceful_shutdown
        config.ALPNProtocols = ["h2", "http/2"]

        print(_config_.__dict__)
        logger.info(json.dumps(_config_.__dict__))
        hypercorn.run.run(_config_)
    else:
        if config.workers and isinstance(config.workers,str) and config.workers.lower()=="auto":
            import psutil
            number_of_workers= psutil.cpu_count(logical=False)
        elif config.workers and isinstance(config.workers,str) and config.workers.isnumeric():
            number_of_workers = int(config.workers)
        elif config.workers and (isinstance(config.workers,int) or isinstance(config.workers,float)):
            number_of_workers = int(config.workers)
        cy_web.start_with_uvicorn(worker=number_of_workers)


