import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.__str__())
import gradio as gr
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build, Resource
import json
import os
def get_google_service(client_id:str,client_secret:str,token:str)->Resource:
    credentials = OAuth2Credentials(
        token=token,
        refresh_token=token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    service = build('drive', 'v3', credentials=credentials)
    return service
def upload_file(client_id:str,client_secret:str,token:str,file_id:str, filepath:str,google_file_name:str):
    """Uploads a new file to Google Drive, replacing the existing file with the same ID.

    Args:
        file_id (str): The ID of the file to be replaced in Google Drive.
        filepath (str): The path to the new file you want to upload.

    Returns:
        The uploaded file metadata dictionary.
    """


    drive_service = get_google_service(client_id,client_secret,token)

    # Set the upload body with the new file

    body = {'name': google_file_name}  # Set the filename from the filepath

    try:
        # Upload the new file, replacing the existing one
        uploaded_file = drive_service.files().update(
            fileId=file_id,
            body=body,
            media_body=filepath
        ).execute()
        return uploaded_file
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def process_text(text):
    try:
        # import requests
        # import os
        data = json.loads(text)
        token= data.get("token")
        app_name = data.get("app_name")
        client_id= data.get('client_id')
        secret_key= data.get('secret_key')
        file_path = data.get('file_path')
        google_folder_id = data.get('folder_id')
        google_file_name= data["google_file_name"]
        google_file_id = data.get('google_file_id')
        url_google_upload = data.get('url_google_upload')
        memcache_server= data.get('memcache_server')
        import cy_file_cryptor.context
        import cy_file_cryptor.wrappers
        # memcache_server="172.16.13.72:11213"
        cy_file_cryptor.context.set_server_cache(data.get('memcache_server'))

        upload_file(
            client_id=client_id,
            client_secret=secret_key,
            token=token,
            file_id=google_file_id,
            filepath=file_path,
            google_file_name = google_file_name
        )

        import cy_file_cryptor.wrappers
        # filesize = os.path.getsize(file_path)
        # headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
        # import mimetypes
        # t, _ = mimetypes.guess_type(file_path)
        # params = {
        #     "name": google_file_name,
        #     "mimeType": t,
        #     "parents":[google_folder_id]
        # }
        # r = requests.post(
        #     "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
        #     headers=headers,
        #     data=json.dumps(params)
        # )
        # location = r.headers['Location']
        # headers = {"Content-Range": f"bytes {0}-{filesize - 1}/{filesize}"}
        # r = requests.put(
        #     location,
        #     headers=headers,
        #     data=open(file_path,"rb"),
        #     stream=True
        # )
        #
        # return r.text
        return google_file_id
    except Exception as ex:
        print(repr(ex))





iface = gr.Interface(
    fn=process_text,
    inputs=["textbox"],
    outputs=["textbox"],
    title="Text Processor",
    description="Enter text and see it processed!",

)
print(f"run on 0.0.0.0:{1116}")
iface.launch(
    server_name="0.0.0.0",  # Here's where you specify server name
    server_port=1116
)

