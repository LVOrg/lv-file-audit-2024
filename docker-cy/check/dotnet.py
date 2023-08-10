import os.path
import pathlib
import sys
sys.path.append("/app")
contents = [
    "noi dung nay dung de kiem tra tinh dung dan cua he thong du doan van ban tieng viet",
    "tien viet so voi tien my re hon. hom nay minh tra tien my bang tien viet",
    "Hom truoc minh vay tien My bang tien My. Hom nay minh tra tien My bang tien Viet",
    "Moi lan an my minh tra tien Viet. Hom nay, minh tra bang tien My",
    "Tien hoc le hau hoc van. Nhung tien hoc le mac hon tien hoc van"

]
from cy_vn import predict_accents, get_config
get_config("/app/share-storage/dataset/cy_vn")

for content in contents:
    ret_content = predict_accents(content)
    print(content)
    print(ret_content.replace('\n',' '))
print("OK")