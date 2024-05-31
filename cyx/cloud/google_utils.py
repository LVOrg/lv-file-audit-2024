import base64
import email.mime.multipart
import email.mime.text
import email.mime.base
import mimetypes
import os
import pathlib
import typing
from fastapi import UploadFile
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ics import Calendar, Event
import starlette.datastructures
import email.encoders as encoders
from datetime import datetime
def create_message(sender, to, cc, subject, body, files:typing.List[UploadFile],calender:UploadFile|None):
    """

    :param sender:
    :param to:
    :param cc:
    :param subject:
    :param body:
    :param files:
    :return: message_body, calendars
    """
    """Creates a MIME message with sender, recipient, subject, body, and attachments."""
    import email.mime.text as mimetext
    import email.mime.multipart as mimemultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    message = mimemultipart.MIMEMultipart()
    message['From'] = sender
    message['To'] = ",".join(to)
    message['Subject'] = subject

    # Add plain text body
    html_part = MIMEText(body, 'html')
    # body_part = mimetext.MIMEText(body, 'html')
    message.attach(html_part)
    if calender:
        attachment_part = MIMEBase('text', 'calendar; method=REQUEST;charset=utf-8')
        # attachment_part = MIMEBase('text', 'calendar;charset=utf-8')
        # ics_content = file.file.read()
        # encoded_content = base64.b64encode(ics_content).decode()

        attachment_part.set_payload(calender.file.read())
        attachment_part.add_header('Content-Disposition', f'attachment; filename="{calender.filename}"')
        message.attach(attachment_part)
    if files:
        for file in files:
            content_type, _ = mimetypes.guess_type(file.filename)
            attachment = email.mime.base.MIMEBase(content_type, 'octet-stream')
            attachment.set_payload(base64.b64encode(file.file.read()))
            attachment.add_header('Content-Disposition', f'attachment; filename="{file.filename}"')
            message.attach(attachment)

    return message, None
    # Add calendar attachment

    # message = email.mime.multipart.MIMEMultipart()
    # message['from'] = sender
    # message['to'] =",".join(to)
    # cc_list  = [x for x in cc if x and len(x)>0]
    # if cc_list:
    #     message['cc'] = ",".join(cc_list)
    # message['subject'] = subject
    # events =[]
    # message.attach(email.mime.text.MIMEText(body, 'plain'))  # Set message body
    # if files:
    #     for file in files or []:
    #         if pathlib.Path(file.filename).suffix==".ics":
    #             calender = Calendar(file.file.read().decode())
    #             tz_name, tz_info = list(calender._timezones.items())[0]
    #             events_list = list( calender.events)
    #             events+=[ convert_event_to_dict(x,tz_name, tz_info) for x in  events_list]
    #
    #         else:
    #             content_type, _ = mimetypes.guess_type(file.filename)
    #             attachment = email.mime.base.MIMEBase(content_type, 'octet-stream')
    #             attachment.set_payload(base64.b64encode(file.file.read()))
    #             attachment.add_header('Content-Disposition', f'attachment; filename="{file.filename}"')
    #             message.attach(attachment)
    #
    # return message, events


def send_message(service, message,user_id="me")->typing.Tuple[dict|None,dict|None]:
    """
    Sends the email message using the Gmail API service. return dict if error

    :param service:
    :param message:
    :param user_id:
    :return:
    """
    """Sends the email message using the Gmail API service."""

    try:
        message_raw = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')
        ret = service.users().messages().send(userId=user_id, body={'raw': message_raw}).execute()


        return ret, None
    except HttpError as error:
        return None, dict(
            Code="GoogleError",
            Description=error.error_details
        )


def create_calendar_event(service, start_datetime, end_datetime, summary, description):
    """Creates a calendar event using the Calendar API."""

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Asia/Ho_Chi Minh',  # Adjust time zone as needed
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Asia/Ho_Chi Minh',
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')  # Get event link for reference
    except HttpError as error:
        print(f'An error occurred: {error}')
def convert_event_to_dict(event:Event,tz_name, tz_info):
    """
    Converts an ics.Event object to a dictionary compatible with Google Calendar API.
    """
    from datetime import timezone
    event_dict = {
        'summary': event.name,
        'description': event.description,
    }
    # Handle start and end date/time with time zone
    if event.begin.datetime is not None:
        start_datetime = event.begin.datetime.astimezone(timezone.utc).isoformat()
        event_dict['start'] = {'dateTime': start_datetime, 'timeZone': tz_name}
    if event.end.datetime is not None:
       end_datetime = event.end.datetime.astimezone(timezone.utc).isoformat()
       event_dict['end'] = {'dateTime': end_datetime, 'timeZone': tz_name}
    return event_dict