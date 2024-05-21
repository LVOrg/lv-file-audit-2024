import typing

import pika
from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)

import pymongo
from cy_controllers.models.file_contents import (
    UploadInfoResult, ParamFileGetInfo,ReadableParam
)
import fastapi.requests
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse, mimetypes
)

router = APIRouter()
controller = Controller(router)
from fastapi.responses import FileResponse
import mimetypes
import cy_docs
import elasticsearch

@controller.resource()
class HealthCheckController(BaseController):

    @controller.route.get(
        "/api/healthz", summary="/healthz",
        tags=["AAA-INFO"]
    )
    async def healthz(self) -> str:
        return "OK version 2.2"

    @controller.route.get(
        "/api/get-info", summary="/healthz",
        tags=["AAA-INFO"]
    )
    async def get_info(self) -> str:
        return os.getenv("PRODUCTION_BUILT_ON") or "dev"
    @controller.route.get(
        "/api/readyz", summary="/readyz",
        tags=["AAA-INFO"]
    )
    async def readyz(self) -> str:

        ret = self.memcache_service.set_str(self.request.url.path,"readyz")
        if ret == 0:
            self.logger_service.error(Exception(
                "cache server fail"
            ),more_info=dict(
                url = self.request.url.path
            ))
            return Response(
                content="cache server fail",
                status_code=500
            )
        es: elasticsearch.Elasticsearch = self.search_engine.client
        try:
            ret = es.ping()
            if ret==False:
                self.logger_service.error(Exception(
                    "elasticsearch fail"
                ), more_info=dict(
                    url=self.request.url.path
                ))
                return Response(
                    content="elasticsearch fail",
                    status_code=500
                )
        except elasticsearch.exceptions.ConnectionError:
            self.logger_service.error(Exception(
                "elasticsearch fail"
            ), more_info=dict(
                url=self.request.url.path
            ))
            return Response(
                content="elasticsearch fail",
                status_code=500
            )
        try:
            client = self.file_service.db_connect.db("admin").__client__
            client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            self.logger_service.error(Exception(
                "No SQL database fail"
            ), more_info=dict(
                url=self.request.url.path,
                mongodb= self.config.db
            ))
            return Response(
                content="No SQL database fail",
                status_code=500
            )
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self.config.rabbitmq.server,
                port=self.config.rabbitmq.port

            ))
            connection.channel().close()
        except pika.exceptions.ConnectionClosedError:
            self.logger_service.error(Exception(
                "message fail"
            ), more_info=dict(
                url=self.request.url.path,
                rabbitmq_server=f"{self.config.rabbitmq.server}:{self.config.rabbitmq.port}"
            ))
            return Response(
                content="message fail",
                status_code=500
            )
        except Exception as e:
            self.logger_service.error(Exception(
                "message fail"
            ), more_info=dict(
                url=self.request.url.path,
                rabbitmq_server=f"{self.config.rabbitmq.server}:{self.config.rabbitmq.port}"
            ))
            return Response(
                content="message fail",
                status_code=500
            )
        return "OK"
