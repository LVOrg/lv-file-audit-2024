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

import cy_docs
from cy_xdoc.auths import Authenticate
import cy_kit
from cyx.common.rabitmq_message import RabitmqMsg

router = APIRouter()
controller = Controller(router)
from cyx.loggers import LoggerService
import cy_web
from cyx.repository import Repository

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
    PageIndex: typing.Optional[int]
from fastapi import Body
from bson.objectid import ObjectId
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
        "/api/logs/views", summary="read log",
        tags=["LOGS"]
    )
    def read_log_async(self,filter:typing.Optional[FilterInfo]=None) :
        """
        "CreatedOn","Content","PodFullName","PodName"
        :param filter:
        :return:
        """
        limit = filter.Limit or 20
        db_context = Repository.lv_files_sys_logs.app("admin")
        filter_from = None
        filter_to = None
        if filter.FormTime:
            filter_from = (
                    (Repository.lv_files_sys_logs.fields.LogOn.year()>=filter.FormTime.year) &
                    (Repository.lv_files_sys_logs.fields.LogOn.month()>=filter.FormTime.month) &
                    (Repository.lv_files_sys_logs.fields.LogOn.day() >= filter.FormTime.day)
                           )
        if filter.ToTime:
            filter_to = (
                    (Repository.lv_files_sys_logs.fields.LogOn.year()<=filter.ToTime.year) &
                    (Repository.lv_files_sys_logs.fields.LogOn.month()<=filter.FormTime.month) &
                    (Repository.lv_files_sys_logs.fields.LogOn.day() <= filter.ToTime.day)
                           )
        filter_time = None
        if filter_from and filter_to:
            filter_time = filter_from & filter_to
        if not filter_from and filter_to:
            filter_time =  filter_to
        if filter_from and not filter_to:
            filter_time =  filter_from
        three_days_ago_utc = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        db_context.context.delete(
            Repository.lv_files_sys_logs.fields.LogOn<three_days_ago_utc
        )
        agg = db_context.context.aggregate()
        if filter_time:
            agg  = agg.match(cy_docs.EXPR(filter_time))
        ret = agg.sort(
            Repository.lv_files_sys_logs.fields.LogOn.desc()
        ).project(
            cy_docs.fields.LogId >> Repository.lv_files_sys_logs.fields.Id,
            cy_docs.fields.CreatedOn >> Repository.lv_files_sys_logs.fields.LogOn,
            cy_docs.fields.PodFullName >> Repository.lv_files_sys_logs.fields.PodId,
            cy_docs.fields.PodName >> Repository.lv_files_sys_logs.fields.PodId,
            cy_docs.fields.Content >> Repository.lv_files_sys_logs.fields.ErrorContent,
            cy_docs.fields.Url >> Repository.lv_files_sys_logs.fields.Url
        ).limit(limit)
        for x in ret:
            yield x.to_json_convertable()

    @controller.route.post(
        "/api/logs/delete", summary="delete log by id",
        tags=["LOGS"]
    )
    def delete_log(self,logId:str=Body(embed=True)):
        db_context = Repository.lv_files_sys_logs.app("admin")
        ret =db_context.context.delete(
            db_context.fields.Id==ObjectId(logId)
        )
        return ret.deleted_count



    @controller.route.post(
        "/api/logs/list-types", summary="list of log type",tags=["LOGS"]
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