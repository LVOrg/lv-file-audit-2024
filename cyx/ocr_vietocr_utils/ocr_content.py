import hashlib
import math
import os.path
import pathlib

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from cyx.ocr_easy_utils import get_all_rectangles, get_skew, rotate
from PIL import Image
import PIL.Image
import numpy
from tqdm import tqdm

if not hasattr(Image, "ANTIALIAS"):
    setattr(Image, "ANTIALIAS", PIL.Image.Resampling.LANCZOS)
package_dir = pathlib.Path(__file__).parent.__str__()
config_dir = os.path.join(package_dir, "config")
from cyx.common import config

os.makedirs(f"/mnt/files/dataset/easyocr", exist_ok=True)
os.makedirs(f"/mnt/files/cacher", exist_ok=True)
import  torch
app_dir= pathlib.Path(package_dir).parent.parent.__str__()
torch_dataset_hub_dir = os.path.join(app_dir,"cy-dataset","torch")
os.makedirs(torch_dataset_hub_dir,exist_ok=True)
easyocr_dataset_hub_dir = os.path.join(app_dir,"cy-dataset","easyocr")
os.makedirs(easyocr_dataset_hub_dir,exist_ok=True)
torch.hub.set_dir(torch_dataset_hub_dir)
def __get_hash_content__(img_src: str):
    with open(img_src, "rb") as f:
        data = f.read()
        hash = hashlib.sha256(data).hexdigest()
        return hash
def ocr_image(img_src: str):
    hash_file = __get_hash_content__(img_src)
    hash_cache_dir = os.path.join(f"/mnt/files/cacher/hash-text/v2")
    os.makedirs(hash_cache_dir,exist_ok=True)
    hash_file_text_content_path=os.path.join(hash_cache_dir,hash_file+".txt")
    if os.path.isfile(hash_file_text_content_path):
        with open(hash_file_text_content_path,"r",encoding="utf8") as fs:
            ret_txt = fs.read()
            return ret_txt

    global_angle = get_skew(img_src)
    ret = get_all_rectangles(img_src, easyocr_dataset_hub_dir, f"/mnt/files/cacher/v2")
    base_config = Cfg.load_config_from_file(os.path.join(config_dir, "base.yml"))
    config = Cfg.load_config_from_file(os.path.join(config_dir, "vgg-transformer.yml"))
    config = {**base_config, **config, 'device': 'cpu'}
    detector = Predictor(config)
    img = Image.open(img_src)
    img_array = numpy.array(img)
    ret_contents = []
    ret_frames = []
    if ret==[]:
        ret=[[(0,0),(0,img.height),(img.width,0),(img.width,img.height)]]
        dy=14
    else:
        dy = min([max([x[1] for x in fx]) - min([x[1] for x in fx]) for fx in ret])
    for i in tqdm(range(len(ret))):
        fx = ret[i]
        x1 = max(min([x[0] for x in fx]),0)
        y1 = max(min([x[1] for x in fx]),0)
        x2 = max(max([x[0] for x in fx]),0)
        y2 = max(max([x[1] for x in fx]),0)
        s=""
        try:
            cropped_image = img_array[y1:y2, x1:x2]
            cropped_im = Image.fromarray(cropped_image)
            s = detector.predict(cropped_im)
        except Exception as e:
            print(e)

        ret_contents += [dict(
            text=s,
            score=math.floor(((y1 + y2) / 2) / dy) * img.width + math.floor(((x1 + x2) / 2) / dy),
            score1=math.floor(((x1 + x2) / 2) / dy) * img.height + math.floor(((y1 + y2) / 2) / dy),

        )]
        ret_frames += [(x1, y1), (x2, y2)]
    if global_angle != 0:
        sorted_list = sorted(ret_contents, key=lambda item: item["score1"])
    else:
        sorted_list = sorted(ret_contents, key=lambda item: item["score"])

    txt = " ".join([x["text"] for x in sorted_list])
    with open(hash_file_text_content_path, "w",encoding="utf-8") as fs:
        fs.write(txt)
    return txt
