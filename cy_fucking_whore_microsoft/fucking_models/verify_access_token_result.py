import typing
from cy_fucking_whore_microsoft.fucking_models.fucking_microsoft_common import BullShitError

import pydantic


class UserInfo(pydantic.BaseModel):
    id: typing.Optional[str]
    displayName: typing.Optional[str]
    surname: typing.Optional[str]
    givenName: typing.Optional[str]
    userPrincipalName: typing.Optional[str]
    preferredLanguage: typing.Optional[str]
    mail: typing.Optional[str]
    businessPhones: typing.Optional[typing.List[str]]


class GetUserInfoResult(pydantic.BaseModel):
    user: typing.Optional[UserInfo]
    error: typing.Optional[BullShitError]
