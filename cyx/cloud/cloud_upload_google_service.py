import typing

import cy_kit
from cyx.g_drive_services import GDriveService
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm
import os
import cy_file_cryptor.context
from cyx.common import config
cy_file_cryptor.context.set_server_cache(config.cache_server)
import cy_file_cryptor.wrappers
class CloudUploadGoogleService:
    def __init__(self,
                 g_drive_service: GDriveService = cy_kit.singleton(GDriveService)):
        self.g_drive_service = g_drive_service

    def do_upload(self, app_name: str, file_path: str, google_file_name: str, google_file_id: str) -> typing.Tuple[
        str | None, dict | None]:
        service, error = self.g_drive_service.get_service_by_app_name(
            app_name=app_name,
            g_service_name="v3/drive"
        )
        if error:
            return None, error
        self.do_upload_by_using_service(service=service,
                                        file_path=file_path,
                                        google_file_name=google_file_name,
                                        google_file_id=google_file_id)
        return google_file_id, None

    def do_upload_by_using_service(self, service, file_path, google_file_name, google_file_id):

        body = {'name': google_file_name}

        # Create a MediaFileUpload object with progress callback
        media_body = MediaFileUpload(file_path, chunksize=1024 * 1024, resumable=True)

        # Initiate the upload request
        request = service.files().update(fileId=google_file_id, body=body, media_body=media_body)
        response = None

        file_size = os.stat(file_path).st_size
        bar = tqdm(total=file_size)
        previous_value = 0
        while response is None:
            status, response = request.next_chunk()
            if status:
                # Print progress bar or update progress bar UI element (implementation not shown here)
                bar.update(status.resumable_progress - previous_value)
                previous_value = status.resumable_progress
        bar.update(file_size)
        return google_file_id
