import io

from cy_file_cryptor import wrappers
import cy_kit
from cyx.local_api_services import LocalAPIService
fs = cy_kit.singleton(LocalAPIService)
token = fs.get_access_token(username="admin/root",password='root')
file_url_1="http://172.16.7.99/lvfile/api/developer/file/9b759c32-6f62-4c67-a644-7cecf160f1dc/signature.png"
file_url="http://172.16.13.72:8012/lvfile/api/lv-docs/file/bf9944cc-63c1-4dd3-91e4-dd6b3c2f3129/acchiles.mp4"
file_url="http://172.16.7.99/lvfile/api/lv-docs/file/7acc2f5b-ad80-46bb-bd41-d56dc1b8bca9/bandicam%202023-08-11%2011-51-55-581.mp4"
# with open(file_url_1,header={"Authorization":f"Bearer {token}"},mode="rb") as fs:
#     fs.seek(10,io.SEEK_CUR)
#     data= fs.read(8)
#     print(data)
import  PIL
from PIL import Image
fx= Image.open(file_url_1)
print(fx)