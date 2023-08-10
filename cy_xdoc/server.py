import json
import pathlib
import sys
import os
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append(os.path.join(pathlib.Path(__file__).parent.parent.__str__(),"cy_core"))
import cyx.common
from cyx.common import config

import fastapi
import datetime
import cy_kit
from cyx.vn_predictor import VnPredictor
vn_pre = cy_kit.singleton(VnPredictor)
txt_non_accent = "Kiem tra he thong Tieng Viet khong dau"
txt_accent  = vn_pre.get_text(txt_non_accent)
print(txt_non_accent)
print(txt_accent)
import cy_web
from cyx.common.msg import MessageService
from cyx.common.brokers import Broker
from cyx.common.rabitmq_message import RabitmqMsg
import cyx.common
config = cyx.common.config
if isinstance(config.get('rabbitmq'),dict):
    cy_kit.config_provider(
            from_class= Broker,
            implement_class= RabitmqMsg
    )

logger = cy_kit.create_logs(
    pathlib.Path(__file__).parent.parent.__str__(),
    "web"
)
print(config)
from cyx.common.base import DbConnect
cnn = cy_kit.singleton(DbConnect)
cnn.set_tracking(True)
cy_web.create_web_app(
    working_dir=pathlib.Path(__file__).parent.__str__(),
    static_dir="./../resource/static",
    template_dir="./../resource/html",
    host_url=config.host_url,
    bind=config.bind,
    cache_folder="./cache",
    dev_mode= cyx.common.config.debug,

)
import asyncio
cy_web.add_cors(["*"])
from starlette.concurrency import iterate_in_threadpool
@cy_web.middleware()
async  def codx_integrate(request:fastapi.Request,next):
    res= await next(request)
    return res

@cy_web.middleware()
async def estimate_time(request:fastapi.Request,next):
    try:
        start_time= datetime.datetime.utcnow()
        res = await next(request)
        if request.url._url==cy_web.get_host_url()+"/api/accounts/token":
            response_body = [chunk async for chunk in res.body_iterator]
            res.body_iterator = iterate_in_threadpool(iter(response_body))
            if len(response_body)>0:
                BODY_CONTENT = response_body[0].decode()

                try:
                    data = json.loads(BODY_CONTENT)
                    if data.get('access_token'):
                        res.set_cookie('access_token_cookie',data.get('access_token'))
                except Exception as e:
                    pass

        end_time = datetime.datetime.utcnow()
        res.headers["time:start"] = start_time.strftime("%H:%M:%S")
        res.headers["time:end"] = end_time.strftime("%H:%M:%S")
        res.headers["time:total(second)"] = (end_time-start_time).total_seconds().__str__()
        res.headers["Server-Timing"] =f"total;dur={(end_time - start_time).total_seconds()*1000}"
    except Exception as e:
        logger.exception(e)
        raise  e

    """HTTP/1.1 200 OK

Server-Timing: miss, db;dur=53, app;dur=47.2"""
    return res

cy_web.load_controller_from_dir("api","./controllers")
cy_web.load_controller_from_dir("","./pages")
app = cy_web.get_fastapi_app()
if __name__ == "__main__":
    cy_web.start_with_uvicorn(worker=int(config.workers or 2))
