import pathlib
import typing

from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

import os


def get_service(token, client_id, client_secret) -> Resource:
    credentials = OAuth2Credentials(
        token=token,
        refresh_token=token,  # Assuming you have a refresh token (optional)
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    service = build('drive', 'v3', credentials=credentials)
    return service


def create_folder(name: str, parent_id: str, service:Resource)->str|None:
    """
  Creates a folder in Google Drive within a specified parent directory.

  Args:
      name (str): Name of the folder to create.
      parent_id (str): ID of the parent directory.
      token (str): Access token for Google Drive API.
      client_id (str): Client ID for Google Drive API.
      client_secret (str): Client Secret for Google Drive API.

  Returns:
      str: ID of the created folder or None if there was an error.
      :param service:
  """
    # Define folder metadata
    folder_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]  # List containing the parent directory ID
    }

    try:
        # Attempt to create the folder
        created_folder = service.files().create(body=folder_metadata).execute()
        return created_folder.get('id')  # Return the ID of the created folder
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None  # Indicate error

def check_folder_exists(subfolders,  service:Resource):
  """
  Checks if a folder exists in Google Drive based on the provided path.

  Args:
      folder_path (str): Path of the folder to check (e.g., /2024/04).
      token (str): Access token for Google Drive API.
      client_id (str): Client ID for Google Drive API.
      client_secret (str): Client Secret for Google Drive API.

  Returns:
      bool: True if the folder exists, False otherwise.
  """



  # Construct the query to search for folders based on the path
  query = "'mimeType' = 'application/vnd.google-apps.folder' and ("

  for folder in subfolders:
    query += f"name = '{folder}' or "
  query = query[:-4] + ')'  # Remove the trailing "or" and add closing parenthesis

  try:
    # Attempt to find the folder using the query
    results = service.files().list(q=query, fields='files(id, name)').execute()
    items = results.get('files', [])
    return bool(items)  # Return True if any folders were found
  except HttpError as error:
    print(f"An error occurred: {error}")
    return False  # Indicate error
def create_folder_structure(subfolders, service:Resource):
    """
  Creates a folder structure in Google Drive based on the provided path in a single API call.

  Args:
      folder_path (str): Path of the folder structure to create (e.g., /2024/04/23/pdf).
      token (str): Access token for Google Drive API.
      client_id (str): Client ID for Google Drive API.
      client_secret (str): Client Secret for Google Drive API.

  Returns:
      str: ID of the final folder in the created structure or None if there was an error.
  """
    # Split the folder path into subfolders
    # Create the first parent directory (if it doesn't exist)
    parent_id = None
    folders_check= []
    dir_id = None
    for folder in subfolders:
        folders_check+=[folder]
        dir_id = get_folders_id(folders_check,service)
        if dir_id:
            parent_id = dir_id
            continue


        folder_metadata = {
            'name': folder,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []  # Set parent if it exists
        }
        try:
            # Attempt to create the folder
            created_folder = service.files().create(body=folder_metadata).execute()
            parent_id = created_folder.get('id')
            dir_id = parent_id
        except HttpError as error:
            if error.resp.status == 409:  # Handle "Folder already exists" error (code 409)
                # Check if the existing folder is the desired one
                content = error.content.decode()
                existing_folder_id = content.split('id": "')[1].split('"')[0]
                existing_folder_name = service.files().get(fileId=existing_folder_id).execute().get('name')
                if existing_folder_name == folder:
                    parent_id = existing_folder_id  # Use existing folder if it matches the desired name
                    print(f"Folder '{folder}' already exists. Using it as parent.")
                else:
                    print(f"An error occurred creating folder '{folder}': {error}")
                    return None  # Indicate error
    return dir_id



def get_folders_id(folders:typing.List[str],service:Resource)->str|None:
    """
  Retrieves the ID of a directory in Google Drive by its name.

  Args:
      name (str): Name of the directory to search for.
      token (str): Access token for Google Drive API.
      client_id (str): Client ID for Google Drive API.
      client_secret (str): Client Secret for Google Drive API.

  Returns:
      str: The ID of the directory or None if not found.
  """
    parent_id= None
    ret= None
    for name in folders:
        # Define query parameters
        if parent_id is None:
            query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        else:
            query = f"mimeType = 'application/vnd.google-apps.folder' and parents = '{parent_id}' and name = '{name}' and trashed = false"

        # Retrieve files and folders matching the query
        results = service.files().list(q=query, fields='files(id, name)').execute()
        items = results.get('files', [])

        # Check if any folders were found
        if items:
            parent_id = items[0]['id']
            ret= items[0]['id']# Return ID of the first matching folder
        else:
            return None  # No folder found
    return ret

from cy_file_cryptor.google_drive_stream import GoogleDriveStream
import mimetypes
def create_upload_stream(file_path: str, token, client_id, client_secret)->GoogleDriveStream:
    credentials = OAuth2Credentials(
        token=token,
        refresh_token=token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    service = build('drive', 'v3', credentials=credentials)
    ret = GoogleDriveStream(
        service=service,
        file_path=file_path

    )

    # metadata = {
    #     'name': os.path.basename(file_path),  # Get filename from path
    #     'mimeType': mime_type,  # Set a generic mimetype (replace if you know the specific type),
    #     'parents': [dir_id]
    # }
    # fx = f"/home/vmadmin/python/cy-py/a-working/files/100 - ELV00767.docx"
    # # Create upload stream
    # media = MediaFileUpload(fx, mimetype=metadata['mimeType'])
    # media.chunksize = 1024 * 1024  # Set chunk size for upload (adjust as needed)
    #
    # result = service.files().create(body=metadata, media_body=media, fields='id').execute()

    return ret
