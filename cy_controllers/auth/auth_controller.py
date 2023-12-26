from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from cy_xdoc.auths import Authenticate
from cyx.common import config

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo


@controller.resource()
class AuthController(BaseController):
    def __init__(self, request: Request):
        self.request = request

    @controller.route.get(
        "/api/{app_name}/auth/check", summary="Re run index search"
    )
    def get_auth(self,app_name:str) -> dict:
        from fastapi import FastAPI, Response
        javascript_code = """
            function myFunction() {
                document.cookie="cy-files-token="""+self.request.query_params['token']+""";domain=172.16.13.72;path=/";
                console.log("Hello from JavaScript!");
            }
            myFunction();
            """
        ret = Response(content=javascript_code, media_type="application/javascript")
        ret.set_cookie("cy-files-token",self.request.query_params['token'])
        return ret
