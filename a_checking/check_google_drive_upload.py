import uuid

import cy_kit
from cyx.common import config
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache("172.16.13.72:11211")

import cy_file_cryptor.wrappers
from cyx.g_drive_services import GDriveService
gs = cy_kit.singleton(GDriveService)
client_id, client_secret,email,error = gs.get_id_and_secret("lv-docs")
token  =gs.get_refresh_access_token("lv-docs")
file_upload=f"/mnt/files/lv-docs/2024/04/24/pdf/b6a0de2a-c597-4aca-bf33-b2c78eec4573/hạ long 3n2đ - saigontourist cap nhat 22 04 2024.pdf"
with open(
        f"google-drive://5fa8baf2b0ec69f914448f53c952bc6d1d3f424cc782451f4b297e444a37c6a5/2024/04/24/pdf/b6a0de2a-c597-4aca-bf33-b2c78eec4573/test-123.pdf",
        "wb",
        token=token,
            client_id=client_id,
            client_secret=client_secret)  as fs:
    fs.write(file_upload)