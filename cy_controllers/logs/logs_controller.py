import datetime
import typing

from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    status,
    Request,
    Response
)
from cy_xdoc.auths import Authenticate
import cy_kit
from cyx.common.rabitmq_message import RabitmqMsg

router = APIRouter()
controller = Controller(router)
from cyx.loggers import LoggerService
import cy_web
@cy_web.model(all_fields_are_optional=True)
class LogInfo:
    CreatedOn: typing.Optional[datetime.datetime]
    Content: typing.Optional[str]
    LogType: typing.Optional[str]
@controller.resource()
class LogsController:
    dependencies = [
        Depends(Authenticate)
    ]
    msg_service = cy_kit.singleton(RabitmqMsg)
    logger_service = cy_kit.singleton(LoggerService)

    def __init__(self, request: Request):
        self.request = request

    @controller.route.post(
        "/api/logs/views", summary="read log"
    )
    def read_log(self)->typing.List[LogInfo]:
        context = self.logger_service.get_mongo_db().context
        fields = self.logger_service.get_mongo_db().fields
        items = context.aggregate().sort(
            fields.CreatedOn.desc()
        ).limit(200)
        ret = [ x.to_pydantic() for x in items ]
        return ret




