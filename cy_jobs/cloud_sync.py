import datetime
import os.path
import pathlib
import time

from cyx.common import config
import cy_docs
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache(config.cache_server)
import cy_file_cryptor.wrappers
import cy_kit
from cyx.repository import Repository
from cyx.g_drive_services import GDriveService
from cyx.local_api_services import LocalAPIService
ls= cy_kit.singleton(LocalAPIService)
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm

from googleapiclient.http import MediaIoBaseDownload
def upload_file_with_progress(drive_service, info, filepath):
  """Uploads a file to Google Drive with a progress bar.

  Args:
      drive_service: The authorized Google Drive service object.
      info: A dictionary containing file information (name, id).
      filepath: The path to the file to upload.

  Returns:
      The uploaded file metadata dictionary.
  """

  # Set the filename
  body = {'name': info['google_file_name']}

  # Create a MediaFileUpload object with progress callback
  media_body = MediaFileUpload(filepath, chunksize=1024 * 1024, resumable=True)

  # Initiate the upload request
  request = drive_service.files().update(fileId=info['file_id'], body=body, media_body=media_body)
  response = None

  file_size = os.stat(filepath).st_size
  bar = tqdm(total=file_size)
  previous_value=0
  while response is None:
    status, response = request.next_chunk()
    if status:
      # Print progress bar or update progress bar UI element (implementation not shown here)
      bar.update(status.resumable_progress-previous_value)
      previous_value=status.resumable_progress


  return response
def update_progress(bytes_uploaded, total_size):
  """Update progress bar based on uploaded bytes and total size (implementation example).

  This is a placeholder function. You'll need to replace it with your preferred progress bar library
  or UI update logic.

  Args:
      bytes_uploaded: The number of bytes uploaded so far.
      total_size: The total size of the file being uploaded.
  """
  # Example using tqdm library (install with 'pip install tqdm')
  from tqdm import tqdm

  progress_bar = tqdm(total=total_size)
  progress_bar.update(bytes_uploaded)
  progress_bar.close()  # Close the progress bar once upload is complete

# ... other code to get drive_service, info, and filepath


while True:
    app_name = "lv-docs"
    g_svc = cy_kit.singleton(GDriveService)

    sync_context = Repository.cloud_file_sync.app(app_name).context
    upload_context = Repository.files.app(app_name).context


    items = sync_context.aggregate().sort(
        Repository.cloud_file_sync.fields.ErrorOn.asc()
    ) .limit(100)
    for x in items:
        drive_service,error = g_svc.get_service_by_app_name(app_name=app_name, g_service_name="v3/drive")
        if error:
            sync_context.update(
                Repository.cloud_file_sync.fields.UploadId==x[Repository.cloud_file_sync.fields.UploadId],
                Repository.cloud_file_sync.fields.IsError << True,
                Repository.cloud_file_sync.fields.ErrorOn << datetime.datetime.utcnow()
            )

        info = upload_context.aggregate().match(
            Repository.files.fields.Id == x[Repository.cloud_file_sync.fields.UploadId]
        ).project(
            cy_docs.fields.google_file_name>> Repository.files.fields.FileName,
            cy_docs.fields.file_id >> Repository.files.fields.google_file_id
        ).first_item()
        upload_item = upload_context.find_one(
            Repository.files.fields.Id== x[Repository.cloud_file_sync.fields.UploadId]
        )
        download_url, rel_path, download_file, token, share_id = ls.get_download_path(upload_item,app_name)
        filepath= os.path.join("/mnt/files",rel_path)
        if os.path.isfile(filepath):
            # body = {'name': info.google_file_name}  # Set the filename from the filepath
            # res = drive_service.files().update(
            #     fileId=info.file_id,
            #     body=body,
            #     media_body=filepath
            # ).execute()

            res = upload_file_with_progress(drive_service, info, filepath)
            if res.get("id"):
                upload_context.update(
                    Repository.files.fields.Id == x[Repository.cloud_file_sync.fields.UploadId],
                    Repository.files.fields.CloudId <<res.get("id")
                )
                sync_context.delete(
                    Repository.cloud_file_sync.fields.UploadId==x.UploadId
                )
                os.remove(filepath)

            else:
                print(res)
        else:
            sync_context.delete(
                Repository.cloud_file_sync.fields.UploadId == x.UploadId
            )

    time.sleep(2)