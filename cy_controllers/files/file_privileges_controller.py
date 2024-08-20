import datetime
import gc
import typing
import uuid

import pydantic
from fastapi_router_controller import Controller
from fastapi import (
    APIRouter,
    Depends,
    Body
)
from cy_xdoc.auths import Authenticate


router = APIRouter()
controller = Controller(router)
import cy_docs

from cy_controllers.common.base_controller import BaseController
from cy_controllers.models.files import (

    AddPrivilegesResult,
    PrivilegesType
)

import cy_web
@controller.resource()
class FilesPrivilegesController(BaseController):
    dependencies = [
        Depends(Authenticate)
    ]
    def file_add_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType]= Body(),
            UploadIds: typing.List[str]= Body()) -> AddPrivilegesResult:
        """
                <p>
                <b>
                    For a certain pair of Application and  Access Token<br/>
                </b>
                    The API allow thou add more list of a privileges tags (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
                    <code>\n
                        //Example add more  accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                        {
                            Data: [
                                        {
                                            Type:'departments',
                                            Values: 'accounting,hr'
                                        },
                                        {
                                            Type:'teams',
                                            Values: 'Codx,xdoC'
                                        }
                                    ],
                            UploadIds:[1,2,3]
                        }
                    </code>


                </p>
                :param app_name:
                :param Data:
                :param UploadIds:
                :param token:
                :return:
                """
        for upload_id in UploadIds:
            ret = self.file_service.add_privileges(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data]

            )
        return AddPrivilegesResult(is_ok=True)

    @controller.router.post("/api/{app_name}/files/remove_privileges",
        tags=["PRIVILEGES"])
    async def remove_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType] = Body(),
            UploadIds: typing.List[str]= Body()) -> AddPrivilegesResult:
        """
        <p>
        <b>
            For a certain pair of Application and  Access Token<br/>
        </b>
            The API allow thou remove list of a privileges tags (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
            <code>\n
                //Example remove accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                {
                    Data: [
                                {
                                    Type:'departments',
                                    Values: 'accounting,hr'
                                },
                                {
                                    Type:'teams',
                                    Values: 'Codx,xdoC'
                                }
                            ],
                    UploadIds:[1,2,3]

                }
            </code>


        </p>
        :param app_name:
        :param Data:
        :param UploadIds:
        :param token:
        :return:
        """
        for upload_id in UploadIds:
            ret = await self.file_service.remove_privileges_async(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data]

            )
        return AddPrivilegesResult(is_ok=True)

    @controller.router.post("/api/{app_name}/files/update_privileges",tags=["PRIVILEGES"])
    def files_update_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType] = Body(),
            UploadIds: typing.List[str] = Body()) -> AddPrivilegesResult:
        """
            <p>
            <b>
                For a certain pair of Application and  Access Token<br/>
            </b>
                The API allow thou remove old list of a privileges tags and set new list of privileges (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
                <code>\n
                    //Example set a new  accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                    {
                        Data: [
                                    {
                                        Type:'departments',
                                        Values: 'accounting,hr'
                                    },
                                    {
                                        Type:'teams',
                                        Values: 'Codx,xdoC'
                                    }
                                ],
                        UploadIds:[1,2,3]
                    }
                </code>


            </p>
            :param app_name:
            :param Data:
            :param UploadIds:
            :param token:
            :return:
            """
        if not app_name:
            app_name = self.request.query_params.get("app_name")
        for upload_id in UploadIds:
            ret = self.file_service.update_privileges(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data],


            )
        return AddPrivilegesResult(is_ok=True)

    @controller.router.post("/api/{app_name}/privileges/update",tags=["PRIVILEGES"])
    def update_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType] = Body(),
            UploadIds: typing.List[str] = Body()) -> AddPrivilegesResult:
        """
            <p>
            <b>
                For a certain pair of Application and  Access Token<br/>
            </b>
                The API allow thou remove old list of a privileges tags and set new list of privileges (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
                <code>\n
                    //Example set a new  accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                    {
                        Data: [
                                    {
                                        Type:'departments',
                                        Values: 'accounting,hr'
                                    },
                                    {
                                        Type:'teams',
                                        Values: 'Codx,xdoC'
                                    }
                                ],
                        UploadIds:[1,2,3]
                    }
                </code>


            </p>
            :param app_name:
            :param Data:
            :param UploadIds:
            :param token:
            :return:
            """
        if not app_name:
            app_name = self.request.query_params.get("app_name")
        for upload_id in UploadIds:
            ret = self.file_service.update_privileges(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data]

            )
        return AddPrivilegesResult(is_ok=True)
    @controller.router.post("/api/{app_name}/privileges/remove",tags=["PRIVILEGES"])
    async def remove_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType] = Body(),
            UploadIds: typing.List[str]= Body()) -> AddPrivilegesResult:
        """
        <p>
        <b>
            For a certain pair of Application and  Access Token<br/>
        </b>
            The API allow thou remove list of a privileges tags (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
            <code>\n
                //Example remove accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                {
                    Data: [
                                {
                                    Type:'departments',
                                    Values: 'accounting,hr'
                                },
                                {
                                    Type:'teams',
                                    Values: 'Codx,xdoC'
                                }
                            ],
                    UploadIds:[1,2,3]

                }
            </code>


        </p>
        :param app_name:
        :param Data:
        :param UploadIds:
        :param token:
        :return:
        """
        for upload_id in UploadIds:
            ret = await self.file_service.remove_privileges_async(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data]

            )
        return AddPrivilegesResult(is_ok=True)

    @controller.router.post("/api/{app_name}/privileges/add",tags=["PRIVILEGES"])
    async def add_privileges(
            self,
            app_name: str,
            Data: typing.List[PrivilegesType] = Body(),
            UploadIds: typing.List[str] = Body()) -> AddPrivilegesResult:
        """
        <p>
        <b>
            For a certain pair of Application and  Access Token<br/>
        </b>
            The API allow thou remove list of a privileges tags (for privileges tags refer to API <i></b>{app_name}/files/register</b></i>) from a list of UploadIds
            <code>\n
                //Example remove accounting department, hr department and teams Codx,xdoC from upload id 1,2,3
                {
                    Data: [
                                {
                                    Type:'departments',
                                    Values: 'accounting,hr'
                                },
                                {
                                    Type:'teams',
                                    Values: 'Codx,xdoC'
                                }
                            ],
                    UploadIds:[1,2,3]

                }
            </code>


        </p>
        :param app_name:
        :param Data:
        :param UploadIds:
        :param token:
        :return:
        """
        for upload_id in UploadIds:
            ret = await self.file_service.add_privileges_async(
                app_name=app_name,
                upload_id=upload_id,
                privileges=[cy_docs.DocumentObject(x) for x in Data]

            )
        return AddPrivilegesResult(is_ok=True)