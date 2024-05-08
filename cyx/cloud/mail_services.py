import typing

import cy_kit
from cyx.cloud.mail_service_google import MailServiceGoogle
from cyx.cloud.mail_service_ms import MailServiceMS

class MailService:
    def __init__(self,
                 google:MailServiceGoogle= cy_kit.singleton(MailServiceGoogle),
                 azure: MailServiceMS = cy_kit.singleton(MailServiceMS)
                 ):
        self.google= google
        self.azure = azure

    def send(self, app_name:str, cloud_name:str, recipient_emails:typing.List[str], cc:typing.List[str], subject:str, body:str, files):
        if cloud_name == "Google":
            ret,error = self.google.send(
                app_name=app_name,
                recipient_emails=recipient_emails,
                cc= cc,
                subject = subject,
                body=body,
                files=files
            )
            if error:
                return  dict(
                    Error = error
                )
            else:
                return  dict(
                    Data = ret
                )
        elif cloud_name=="Azure":
            return self.azure.send(
                app_name=app_name,
                recipient_emails=recipient_emails,
                cc=cc,
                subject=subject,
                body=body,
                files=files
            )
