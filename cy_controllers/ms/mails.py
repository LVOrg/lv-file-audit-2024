import typing

from fastapi_router_controller import Controller
import cy_xdoc.models.files
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Body,
    UploadFile,
    File

)

import cyx.common.msg
from cy_controllers.models.file_contents import (
    UploadInfoResult, ParamFileGetInfo, ReadableParam
)
import fastapi.requests
import cy_web
import os
from cy_controllers.common.base_controller import (
    BaseController, FileResponse, mimetypes
)

router = APIRouter()
controller = Controller(router)

from cy_xdoc.auths import Authenticate
@controller.resource()
class MSMail(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    @controller.router.post(
        path="/api/{app_name}/ms/mail/send"
    )
    def mail_send(self,app_name:str,recipient_email:str=Body(embed=True), subject:str=Body(embed=True), body:str=Body(embed=True),
                  file:  typing.Annotated[UploadFile | None, File(description="Some description")] = None):
        data  = {
              "message": {
                  "subject": subject,
                  "body": {
                      "content": body,
                      "contentType": "Text"  # Can be "Html" for HTML content
                  },
                  "toRecipients": [
                      {"emailAddress": {"address": recipient_email}}
                  ],
                  # "Attachments": [
                  #     {
                  #         "Name": "attachment.txt",  # Replace with your actual filename
                  #         "ContentBytes": attachment_content.decode("utf-8"),  # Base64 encoding not needed
                  #         "ContentType": "text/plain"  # Set content type based on attachment type
                  #     }
                  # ]
              }
          }
        content_type=None



        if file:
            import base64
            data["message"]["attachments"]= [
                      {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": file.filename,
                        "contentType": file.content_type,
                        "contentBytes":base64.b64encode(file.file.read() ).decode("utf-8")
                      }
                    ]

        ret,error = self.ms_common_service.call_graph_api(
            app_name=app_name,
            method="post",
            grap_api="me/sendMail",
            data=data,
            content_type=content_type
        )
        if error:
            return error
        else:
            return ret