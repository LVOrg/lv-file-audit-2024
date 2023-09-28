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
    PodFullName: typing.Optional[str]
    PodName: typing.Optional[str]
@cy_web.model(all_fields_are_optional=True)
class FilterInfo:
    FormTime: typing.Optional[datetime.datetime]
    ToTime: typing.Optional[datetime.datetime]
    LogType: typing.Optional[str]
    Instance: typing.Optional[str]
    Limit: typing.Optional[int]

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
    def read_log(self,filter:typing.Optional[FilterInfo]=None) -> typing.List[LogInfo]:
        context = self.logger_service.get_mongo_db().context
        fields = self.logger_service.get_mongo_db().fields
        filter_expr = None
        limit = 50
        if filter is not  None:
            if filter.Limit is not None:
                limit = filter.Limit
            if filter.LogType is not None:
                filter_expr = (fields.LogType==filter.LogType) & filter_expr
            if filter.Instance is not None:
                filter_expr = (fields.PodName==filter.Instance) & filter_expr
            if filter.FormTime is not None:
                filter_expr = (fields.CreatedOn >= datetime.datetime.combine(filter.FormTime.date(),datetime.time(0,0,0))) & filter_expr
            if filter.ToTime is not None:
                filter_expr = (fields.CreatedOn >= datetime.datetime.combine(filter.ToTime.date(),datetime.time(0,0,0))) & filter_expr

        if filter_expr is None:
            items = context.aggregate().sort(
                fields.CreatedOn.desc()
            ).limit(limit)
            ret = [x.to_pydantic() for x in items]
            return ret
        else:
            items = context.aggregate().sort(
                fields.CreatedOn.desc()
            ).match(
                filter = filter_expr
            ).limit(limit)
            ret = [x.to_pydantic() for x in items]
            return ret

    @controller.route.post(
        "/api/logs/list-types", summary="list of log type"
    )
    def get_log_type(self)->typing.List[dict]:
        db = self.logger_service.get_mongo_db()
        context = self.logger_service.get_mongo_db().context
        ret = context.aggregate().group(
            db.fields.LogType
        )
        return list(ret)

    @controller.route.post(
        "/api/logs/list-instance", summary="list of log type"
    )
    def get_log_instance(self) -> typing.List[dict]:
        db = self.logger_service.get_mongo_db()
        context = self.logger_service.get_mongo_db().context
        ret = context.aggregate().group(
            db.fields.PodName
        )
        return list(ret)