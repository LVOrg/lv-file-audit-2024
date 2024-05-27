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
import re
@controller.resource()
class CloudMailController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    # dependencies = [
    #     Depends(Authenticate)
    # ]
    @controller.router.post(
        path="/api/{app_name}/cloud/mail/send",
        tags = ["CLOUD"]
    )
    async def cloud_mail_send_async(self,
                        app_name:str,
                        cloud_name:str = Body(embed=True,description="value must be 'Google','Azure' or 'AWS'"),
                        recipient_emails:str=Body(embed=True,description="list of email to send, seperated by '.'"),
                        cc:str = Body(embed=True,default=None,description="CC to"),
                        subject:str=Body(embed=True),
                        body:str=Body(embed=True),
                        files:  list[UploadFile] = File(...),
                        uploadIds:typing.Optional[str]=Body(default=None,description="Attachmnet by uploadId. "
                                                                                             "Given text seperated by"
                                                                                             " comma"),
                        calender: typing.Optional[UploadFile]= File(None)):
        """
        :param uploadIds: text with separated by comma
        :param app_name:
        :param cloud_name: value must be 'Google','Azure' or 'AWS'
        :param recipient_email: Separated by comma Ex: user1@mail-server.com, user2@mail-server.com,...
        :param subject:
        :param body:
        :param files:
        :return:
        """
        regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"

        if cloud_name not in ['Google','Azure' , 'AWS']:
            return dict(
                result= None,
                error = dict(
                    Code="InvalidValue",
                    Description=f"'{cloud_name}' must be 'Google','Azure' or 'AWS' "
                )
            )

        if not self.cloud_service_utils.is_ready_for(app_name,cloud_name):
            return dict(
                result=None,
                error=dict(
                    error="CloudLinkError",
                    description=f"'{cloud_name}' did not bestow {app_name} yet"
                )
            )
        recipient_emails = recipient_emails.split(',')
        invalid_emails = [x for x in recipient_emails if not re.match(regex, x)]
        if len(invalid_emails)>0:
            return dict(
                error=dict(
                    Code="InvalidEmail",
                    Description=f"{','.join(invalid_emails)} is invalid email"
                )
            )
        self.cloud_service_utils.mail_service.send(
            app_name=app_name,
            cloud_name=cloud_name,
            recipient_emails=recipient_emails,
            cc=(cc or "").split(','),
            subject=subject,
            body = body,
            files = files,
            calender = calender

        )