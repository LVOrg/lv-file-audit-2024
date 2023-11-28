import typing


class AccInfo:
    displayName: typing.Optional[str]
    businessPhones: typing.Optional[typing.List[str]]
    givenName: typing.Optional[str]
    jobTitle: typing.Optional[str]
    mobilePhone: typing.Optional[str]
    officeLocation: typing.Optional[str]
    preferredLanguage: typing.Optional[str]
    surname: typing.Optional[str]
    userPrincipalName: typing.Optional[str]
    id: typing.Optional[str]


class AccountService:
    def __init__(self):
        pass

    def get_current_acc_info(self, access_token) -> AccInfo:
        """
        The shit function use for current account info getting from Whore-Microsoft-Online
        :param access_token:
        :return:
        """
        from cy_azure.fwcking_ms.caller import call_ms_func
        return call_ms_func(
            api_url="me",
            token=access_token,
            body=None,
            method="get",
            request_content_type=None,
            return_type=AccInfo
        )
