import typing

from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body

)
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
        "/api/healthz", summary="/healthz"
    )
    async def healthz(self) -> str:
        return "OK"

    @controller.route.get(
        "/api/readyz", summary="/readyz"
    )
    async def readyz(self) -> str:

        ret = self.memcache_service.set_str(self.request.url.path,"readyz")
        if ret == 0:
            return Response(
                content="cache server fail",
                status_code=500
            )
        es: elasticsearch.Elasticsearch = self.search_engine.client
        try:
            ret = es.ping()
            if ret==False:
                return Response(
                    content="elasticsearch fail",
                    status_code=500
                )
        except elasticsearch.exceptions.ConnectionError:
            return Response(
                content="elasticsearch fail",
                status_code=500
            )

        return "OK"
