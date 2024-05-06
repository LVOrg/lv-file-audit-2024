import base64

import cy_kit
from  cyx.g_drive_services import GDriveService
g= cy_kit.singleton(GDriveService)
def create_message(sender, to, subject, body):
  """
  Creates a dictionary representing the email message structure.
  """
  message = {
      'raw': base64.urlsafe_b64encode(
          f"From: {sender}\nTo: {to}\nSubject: {subject}\n\n{body}".encode('utf-8')
      ).decode('utf-8')
  }
  return message

service = g.get_service_by_app_name("lv-docs",g_service_name="v1/gmail")
def send_email(service, user_id, message):
  """
  Sends an email using the provided service object and message structure.
  """
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print(f'Message Id: {message["id"]}')
  except Exception as e:
    print(f'Error sending email: {e}')
user_id = 'me'
sender = "the886717@gmail.com"
to = "tqhoan@lacviet.com.vn"
subject = "Test Email from Your App"
body = "This is a test email sent from your Google App."
# access_token =  g.get_access_token_from_refresh_token("lv-docs")
from googleapiclient.discovery import build
message = create_message(sender, to, subject, body)
send_email(service, user_id, message)