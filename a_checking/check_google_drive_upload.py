import cy_kit
from cyx.common import config
import cy_file_cryptor.wrappers
from cyx.g_drive_services import GDriveService
gs = cy_kit.singleton(GDriveService)
client_id, client_secret = gs.get_id_and_secret("lv-docs")
token  =gs.get_refresh_access_token("lv-docs")
with open("google://long_test.png","rb", token=token,
            client_id=client_id,
            client_secret=client_secret)  as fs:
    fs.write("dsadas")