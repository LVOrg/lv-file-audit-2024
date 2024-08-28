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
    Form,
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
from  pydantic import BaseModel
class DataInfo(BaseModel):
    Question: typing.Annotated[str|None,Form()]
    FormatText:typing.Annotated[str|None,Form()]
    OutpuType:typing.Annotated[str|None,Form()]
@controller.resource()
class GeminiControllr(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]

    @controller.router.post("/api/global/gemini")
    async def upload_file(self,
                          file:UploadFile|None = File(default=None),
                          question: str|None = Form(default=None),
                          format_content: str|None = Form(default=None),
                          return_format: str|None = Form(default=None)
                          ):
        """
        Upload a file and optionally send a text message.

        Args:
            file: The uploaded file (required).
            text: Optional text message.

        Returns:
            A dictionary containing information about the uploaded file and the received text.
        """
        res = None
        try:
            tmp_gemini_dir =os.path.join(self.config.file_storage_path,"__gemini_tmp__")
            os.makedirs(tmp_gemini_dir,exist_ok=True)
            tmp_file = os.path.join(tmp_gemini_dir,str(uuid.uuid4()))
            if file is not None:
                contents = await file.read()  # Read the entire file content
                with open(tmp_file, "wb") as buffer:
                    buffer.write(contents)  # Write the content to the specified location
                is_image = file.content_type.startswith("image/")
                res = self.gemini_service.get_text(
                    file_path = tmp_file,
                    is_image = is_image,
                    format_content=format_content,
                    output= return_format or "JSON",
                    question= question

                )

            else:
                res = self.gemini_service.get_text(
                    format_content=format_content,
                    output=return_format,
                    question=question

                )

            return dict(
                result=res
            )
        except Exception as e:
            return  dict(
                error=dict(
                    code="System",
                    message = str(e)
                )
            )