import pathlib
import typing
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
import os
import mimetypes
from io import BytesIO


class GoogleDriveStream:
    def __init__(self, service: Resource, file_path: str):
        self.service = service
        self.file_path = file_path
        self.dirs = file_path.split("://")[1].split('/')[:-1]
        self.filename = os.path.basename(file_path)
        self.dir_id = self.create_folder_structure(self.dirs)
        mime_type, _ = mimetypes.guess_type(file_path)
        self.mime_type = mime_type

    def create_folder_structure(self, subfolders: typing.List[str]):
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
        folders_check = []
        dir_id = None
        for folder in subfolders:
            folders_check += [folder]
            dir_id = self.get_folders_id(folders_check)
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
                created_folder = self.service.files().create(body=folder_metadata).execute()
                parent_id = created_folder.get('id')
                dir_id = parent_id
            except HttpError as error:
                if error.resp.status == 409:  # Handle "Folder already exists" error (code 409)
                    # Check if the existing folder is the desired one
                    content = error.content.decode()
                    existing_folder_id = content.split('id": "')[1].split('"')[0]
                    existing_folder_name = self.service.files().get(fileId=existing_folder_id).execute().get('name')
                    if existing_folder_name == folder:
                        parent_id = existing_folder_id  # Use existing folder if it matches the desired name
                        print(f"Folder '{folder}' already exists. Using it as parent.")
                    else:
                        print(f"An error occurred creating folder '{folder}': {error}")
                        return None  # Indicate error
        return dir_id

    def get_folders_id(self, folders: typing.List[str]) -> str | None:
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
        parent_id = None
        ret = None
        for name in folders:
            # Define query parameters
            if parent_id is None:
                query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            else:
                query = f"mimeType = 'application/vnd.google-apps.folder' and parents = '{parent_id}' and name = '{name}' and trashed = false"

            # Retrieve files and folders matching the query
            results = self.service.files().list(q=query, fields='files(id, name)').execute()
            items = results.get('files', [])

            # Check if any folders were found
            if items:
                parent_id = items[0]['id']
                ret = items[0]['id']  # Return ID of the first matching folder
            else:
                return None  # No folder found
        return ret

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def write(self, data)->str|None:
        if isinstance(data, bytes):
            file_data = BytesIO(data)
            media_body = MediaIoBaseUpload(file_data, mimetype=self.mime_type, resumable=True)
        if isinstance(data, str):

            media_body = MediaFileUpload(data, mimetype=self.mime_type, resumable=True)
        body = {
            'name': self.filename,
            'parents': [self.dir_id]  # Replace with the ID of the target folder
        }

        # Upload the binary data
        try:
            request = self.service.files().create(body=body, media_body=media_body)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print('Uploaded %d%%.' % int(status.progress() * 100))
            return response.get('id')
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
