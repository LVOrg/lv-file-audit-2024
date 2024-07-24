from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    Form,
    Query,
Path

)
from typing import Annotated
from cy_xdoc.auths import Authenticate
from cyx.common import config

router = APIRouter()
controller = Controller(router)
from cy_controllers.common.base_controller import BaseController
import pymongo
from fastapi import FastAPI, Request, Response

import requests
@controller.resource()
class NoteBookController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    def __init__(self, request: Request):
        self.request = request

    @controller.route.get(
        "/note-book{path:path}", summary="Re run index search"
    )
    async def get_config(self, path: str) -> dict:
        request=self.request
        try:
            # Construct the complete target URL with the requested path
            target_request_url = f"http://172.16.13.72:8019/{path}"

            # Forward the request with headers and body (if applicable)
            response = requests.request(
                method=request.method,
                url=target_request_url,
                headers=request.headers,
                data=await request.body(),  # Include request body if necessary
            )
            response.raise_for_status()

            # Create a FastAPI response with the same status code and headers
            fastapi_response = Response(content=response.content, status_code=response.status_code)
            for header, value in response.headers.items():
                fastapi_response.headers[header] = value

            return fastapi_response

        except requests.exceptions.RequestException as e:
            # Handle exceptions gracefully (e.g., log error, return error message)
            return Response(content=str(e).encode(), status_code=500)