import datetime
import typing
from cy_controllers.models.errors import ErrorResult
from pydantic import BaseModel


class AppMicrosoftAzure(BaseModel):
    """
    Info map from Microsoft Azure
    Goto https://entra.microsoft.com locate App Registration obtain whole info
    """
    Name: typing.Optional[str]
    ClientId: typing.Optional[str]
    TenantId: typing.Optional[str]
    UrlLogin: typing.Optional[str]
    ClientSecret: typing.Optional[str]
    IsPersonal: typing.Optional[bool]
    AccessToken: typing.Optional[str]
    RefreshToken: typing.Optional[str]
    TokenId: typing.Optional[str]
    AuthCode: typing.Optional[str]
    PersonalAccountUrlLogin: typing.Optional[str]
    BusinessAccountUrlLogin: typing.Optional[str]

class AppsOnCloud(BaseModel):
    """
    Info map an application from Cloud such as Microsoft Azure, Google App, AWS,..
    """
    Azure: typing.Optional[AppMicrosoftAzure]


class AppInfo(BaseModel):
    """
    Infomation of application, an application is one-one mapping to tanent
    """
    AppId: typing.Optional[str]
    """
    The __name__ of application
    """
    Name: str
    Description: typing.Optional[str]
    Domain: typing.Optional[str]
    LoginUrl: typing.Optional[str]
    ReturnUrlAfterSignIn: typing.Optional[str]
    ReturnSegmentKey: typing.Optional[str]
    RegisteredOn: typing.Optional[datetime.datetime]
    LatestAccess: typing.Optional[datetime.datetime]
    AccessCount: typing.Optional[int]
    AppOnCloud: typing.Optional[AppsOnCloud]
    AzureLoginUrl: typing.Optional[str]
    SizeInGB: typing.Optional[float]


class AppInfoRegister(AppInfo):
    UserName: typing.Optional[str]
    """
    Co cung dc kg co cung khong sao
    """
    Password: typing.Optional[str]


class AppInfoRegisterModel(BaseModel):
    Data: typing.Optional[AppInfoRegister]


class AppInfoRegisterResult(BaseModel):
    Data: typing.Optional[AppInfo]
    Error: typing.Optional[ErrorResult]

