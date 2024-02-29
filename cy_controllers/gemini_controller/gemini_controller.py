import mimetypes
import os
import typing
import uuid

import cy_web
from fastapi import (
    APIRouter,
    Depends,
    Body,
    File,
    UploadFile
)
from cy_controllers.common.base_controller import BaseController
import pydantic
from fastapi_router_controller import Controller

router = APIRouter()
controller = Controller(router)
from cy_xdoc.auths import Authenticate
from cy_controllers.models.global_settings import SettingInfo
from cyx.repository import Repository

@controller.resource()
class GeminiControllr(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/global/gemini")
    async def upload_file(self,file: UploadFile = File(...), text: typing.Optional[str] = None):
        """
        Upload a file and optionally send a text message.

        Args:
            file: The uploaded file (required).
            text: Optional text message.

        Returns:
            A dictionary containing information about the uploaded file and the received text.
        """
        tmp_gemini_dir =os.path.join(self.config.file_storage_path,"__gemini_tmp__")
        os.makedirs(tmp_gemini_dir,exist_ok=True)
        tmp_file = os.path.join(tmp_gemini_dir,str(uuid.uuid4()))
        contents = await file.read()  # Read the entire file content
        with open(tmp_file, "wb") as buffer:
            buffer.write(contents)  # Write the content to the specified location
        is_image = file.content_type.startswith("image/")
        res = self.gemini_service.get_text(
            file_path = tmp_file,
            is_image = is_image,
            text = text
        )
        return res