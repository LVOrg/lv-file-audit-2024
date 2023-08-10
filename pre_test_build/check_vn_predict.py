import pathlib
_wrking_dir_ = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(_wrking_dir_)
from cyx.vn_predictor import VnPredictor
import cy_kit
instance =cy_kit.singleton(VnPredictor)
contents = [
    "noi dung nay dung de kiem tra tinh dung dan cua he thong du doan van ban tieng viet",
    "tien viet so voi tien my re hon. hom nay minh tra tien my bang tien viet",
    "Hom truoc minh vay tien My bang tien My. Hom nay minh tra tien My bang tien Viet",
    "Moi lan an my minh tra tien Viet. Hom nay, minh tra bang tien My",
    "Tien hoc le hau hoc van. Nhung tien hoc le mac hon tien hoc van"

]
for content in contents:
    ret_content = instance.get_text(content)
    print(content)
    print(ret_content.replace('\n',' '))
print("OK")