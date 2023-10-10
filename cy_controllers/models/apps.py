import datetime
import typing
import cy_web
from cy_xdoc.controllers.models.errors import ErrorResult
from pydantic import BaseModel
class AppInfo(BaseModel):
    """
    Infomation of application, an application is one-one mapping to tanent
    """
    AppId:typing.Optional[str]
    """
    The __name__ of application
    """
    Name:str
    Description: typing.Optional[str]
    Domain: typing.Optional[str]
    LoginUrl:typing.Optional[str]
    ReturnUrlAfterSignIn:typing.Optional[str]
    ReturnSegmentKey:typing.Optional[str]
    RegisteredOn: typing.Optional[datetime.datetime]
    LatestAccess: typing.Optional[datetime.datetime]
    AccessCount: typing.Optional[int]
from pydantic import Field


class AppInfoRegister(AppInfo):

    UserName: typing.Optional[str]
    """
    Co cung dc kg co cung khong sao
    """
    Password: typing.Optional[str]

class AppInfoRegisterModel(BaseModel):
    Data: typing.Optional[AppInfoRegister]

class AppInfoRegisterResult(BaseModel):
    Data:typing.Optional[AppInfo]
    Error:typing.Optional[ErrorResult]

