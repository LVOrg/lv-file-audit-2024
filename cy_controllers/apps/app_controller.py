import datetime

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


@controller.resource()
class AppsController:
    dependencies = [
        Depends(Authenticate)
    ]
    msg_service = cy_kit.singleton(RabitmqMsg)

    def __init__(self, request: Request):
        self.request = request

    @controller.route.post(
        "/api/apps/{app_name}/re_index", summary="Re run index search"
    )
    def re_index(self,app_name:str)->str:
        import cyx.common.msg
        self.msg_service.emit(
            app_name = app_name,
            message_type=cyx.common.msg.MSG_APP_RE_INDEX_ALL,
            data = dict(
                app_name = app_name,
                emit_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )

        )
        return app_name

