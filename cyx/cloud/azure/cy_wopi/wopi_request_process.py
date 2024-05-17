import uuid

import fastapi.requests

import cy_kit
from cyx.cy_wopi import wopi_request
from cy_xdoc.services.files import FileServices


class HttpContext:
    request: fastapi.requests.Request

    def __init__(self):
        self.request


class ProcessWopiRequestService:
    def __init__(self, file_service=cy_kit.singleton(FileServices)):
        self.file_services = file_service

    def process_request(self, context: HttpContext):
        request = wopi_request.parse_request(context.request)
        response = None

        try:
            pass
        except Exception as e:
            pass
