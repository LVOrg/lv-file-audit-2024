import typing

import cy_kit
from cyx.g_drive_services import GDriveService
from cyx.cloud import google_utils
from fastapi import UploadFile

class MailServiceGoogle:
    def __init__(self, g_drive_service: GDriveService = cy_kit.singleton(GDriveService)):
        self.google_auth_service = g_drive_service

    def send(self,
             app_name: str,
             recipient_emails: typing.List[str],
             subject: str,
             body: str,
             files:typing.Union[typing.List[UploadFile],None]=None,
             calender: typing.Union[UploadFile,None]=None,
             cc: typing.Union[typing.List[str], None] = None) -> typing.Tuple[typing.Union[dict, None], typing.Union[dict, None]]:

        service, error = self.google_auth_service.get_service_by_app_name(
            app_name=app_name,
            g_service_name="v1/gmail"
        )
        # service_events, error = self.google_auth_service.get_service_by_app_name(
        #     app_name=app_name,
        #     g_service_name="v1/gmail"
        # )
        client_id, client_secret, email, error = self.google_auth_service.get_id_and_secret(app_name)
        if error:
            return None, error
        if error:
            return None, error
        message, events = google_utils.create_message(
            sender=email,
            to=recipient_emails,
            cc=cc,
            subject=subject,
            body= body,
            files=files,
            calender=calender


        )
        ret,error = google_utils.send_message(service,message)
        return ret,error
