"""
This file declare all info for web api start
"""

import functools
import json
import pathlib
import sys
import os
import traceback
import psutil

WORKING_DIR = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(pathlib.Path(__file__).parent.parent)
"""
For IIS host or dev mode running add current directory into sys. That will help Python load all libraries in the same applications
"""
sys.path.append("/app")
"""
add directory of all libs. When run on docker or K8S all source code deployment will be placed in /app directory
"""

from cyx.cache_service.memcache_service import MemcacheServices

import cy_kit

memcache_services = cy_kit.singleton(MemcacheServices)
memcache_services.check_connection(3600)
from cyx.file_utils_services import FileUtilService

file_util_service = cy_kit.singleton(FileUtilService)

from cyx.runtime_config_services import RuntimeConfigService

runtime_config_service = cy_kit.singleton(RuntimeConfigService)
runtime_config_service.load(sys.argv)
skip_checking = os.getenv("BUILD_IMAGE_TAG") is None


from fastapi.responses import Response
import cyx.common
from cyx.common import config

version2 = config.generation if hasattr(config, "generation") else None
file_util_service.healthz() if version2 else print("Run firs generation")
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

from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cyx.common
from fastapi.middleware.gzip import GZipMiddleware

config = cyx.common.config

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
config.server_type = "Uvicorn"
config.worker_class = "httptools"
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

accept_domains = ["*"]
if hasattr(config, "domains"):
    accept_domains = config.domains.split(",")
cy_web.add_cors(accept_domains)
from starlette.concurrency import iterate_in_threadpool

@functools.cache
def get_pod_name():
    f = open('/etc/hostname')
    pod_name = f.read()
    f.close()
    full_pod_name = pod_name.lstrip('\n').rstrip('\n')
    return full_pod_name


from cyx.logs_to_mongo_db_services import LogsToMongoDbService
from fastapi.responses import JSONResponse
from cyx.malloc_services import MallocService

malloc_service = cy_kit.singleton(MallocService)
logs_to_mongo_db_service = cy_kit.singleton(LogsToMongoDbService)


async def dev_mode(request: fastapi.Request, next):
    start_time = datetime.datetime.utcnow()
    try:
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
        # build-22.20240809144938
        end_time = datetime.datetime.utcnow()

        async def apply_time(res):
            res.headers["Server-Timing"] = f"total;dur={(end_time - start_time).total_seconds() * 1000}"
            return res

        res = await apply_time(res)
        return res
    except Exception as ex:
        return Response(content=traceback.format_exc(),status_code=500)


async def release_mode(request: fastapi.Request, next):
    orgigin = None
    try:

        if request.headers.get("origin") or request.headers.get("Origin"):
            orgigin = request.headers.get("origin") or request.headers.get("Origin")
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
        #build-22.20240809144938
        end_time = datetime.datetime.utcnow()

        async def apply_time(res):
            res.headers["Server-Timing"] = f"total;dur={(end_time - start_time).total_seconds() * 1000}"
            return res

        res = await apply_time(res)
        if orgigin:
            #response.Headers.Append("Access-Control-Allow-Origin", value);
            res.headers["access-control-allow-origin"] = orgigin
        # else:
        #     res.headers["access-control-allow-origin"] = "https://oms.qtsc.com.vn"
        res.headers['access-control-allow-credentials'] = 'true'
        return res
    except Exception as ex:
        error_content = traceback.format_exc()

        await logs_to_mongo_db_service.log_async(error_content, request.url.path)

        ret_error = dict(
            Error=dict(
                Code="System",
                Message=error_content
            )
        )
        if config.debug == True:
            res = JSONResponse(content=ret_error, status_code=200)
            if orgigin:

                res.headers["access-control-allow-origin"] = orgigin
            res.headers['access-control-allow-credentials'] = 'true'
            return res
        else:
            res = JSONResponse(content="Error on server", status_code=500)
            res.headers['access-control-allow-credentials'] = 'true'
            return res
    finally:
        malloc_service.reduce_memory()


is_dev_mode = hasattr(config, "is_dev_mode")


@cy_web.middleware()
async def estimate_time(request: fastapi.Request, next):
    try:
        if is_dev_mode:
            return await dev_mode(request, next)
        else:
            return await release_mode(request, next)
    except FileNotFoundError():
        return Response(status_code=404,content="Resource was not found")


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


number_of_workers = get_number_of_cpus()[0]
if config.workers != "auto":
    if isinstance(config.workers, int):
        number_of_workers = config.workers
    else:
        number_of_workers = 1

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


config.server_type = "default"

if __name__ == "__main__":
    if sys.platform in ["win32", "win64"]:
        """
        If run on windows only support hypercorn
        """
        config.server_type = "hypercorn"
    if config.server_type.lower() == "gunicorn":
        from gunicorn import workers
        config.worker_class = "gthread"
        options = {
            "bind": "%s:%s" % (cy_app_web.bind_ip, cy_app_web.bind_port),
            "workers": number_of_workers,
            "worker_class": config.worker_class,
            "timeout_keep_alive": 30,
            "timeout_graceful_shutdown": 10
        }
        print(options)

        if not sys.platform in ["win32", "win64"]:
            from cy_web.standalone_application import StandaloneApplication

            StandaloneApplication(app, options).run()
    elif config.server_type == "hypercorn":
        import hypercorn.config, hypercorn.run

        _config_ = hypercorn.config.Config()
        _config_.bind = [f"{cy_app_web.bind_ip}:{cy_app_web.bind_port}"]
        _config_.application_path = "cy_web:get_fastapi_app()"


        number_of_workers = psutil.cpu_count(logical=False) // 2
        _config_.workers = number_of_workers
        _config_.keep_alive_timeout = config.timeout_keep_alive
        if config.h2_max_concurrent_streams != "auto":
            _config_.h2_max_concurrent_streams = config.h2_max_concurrent_streams
        _config_.worker_class = "asyncio"
        if config.timeout_graceful_shutdown != "auto":
            _config_.shutdown_timeout = config.timeout_graceful_shutdown
        config.ALPNProtocols = ["h2", "http/2"]

        print(_config_.__dict__)
        logger.info(json.dumps(_config_.__dict__))
        hypercorn.run.run(_config_)
    else:
        if config.workers and isinstance(config.workers, str) and config.workers.lower() == "auto":


            number_of_workers = psutil.cpu_count(logical=False)
        elif config.workers and isinstance(config.workers, str) and config.workers.isnumeric():
            number_of_workers = int(config.workers)
        elif config.workers and (isinstance(config.workers, int) or isinstance(config.workers, float)):
            number_of_workers = int(config.workers)

        cy_web.start_with_uvicorn(worker=number_of_workers)

#helm install kestra kestra/kestra --namespace kestra
