import math
import os.path

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from cyx.ocr_easy_utils import get_all_rectangles,get_skew,rotate
from PIL import Image
import PIL.Image
import numpy
from tqdm import tqdm
if not hasattr(Image,"ANTIALIAS"):
    setattr(Image,"ANTIALIAS",PIL.Image.Resampling.LANCZOS)
file_test=f"/mnt/files/developer/2023/09/26/pdf/bc61ab45-5308-43a7-bbd7-7630f5c1e0d5/pdf_images/page_0000.png"
file_test=f"/mnt/files/lacvietdemo/2024/01/08/png/094353ad-2717-4d59-a3b3-4bff941cb466/6.png"
file_test=f"/mnt/files/lacvietdemo/2024/01/02/png/2db9cca0-a04a-410e-81b3-2b3848d5e441/appstore.png"
file_test=f"/mnt/files/lacvietdemo/2023/12/28/jpg/37818fd1-3c03-4f01-b588-9936f397c3c4/8bf058fe053a152f0854badcc8bce242_1_.jpg"
file_test_out=f"/mnt/files/lacvietdemo/2023/12/28/jpg/37818fd1-3c03-4f01-b588-9936f397c3c4/result.jpg"
file_test=f"/mnt/files/lacvietdemo/2023/12/28/jpg/bc02b962-94e8-4d88-a4d8-3c17306bb0a1/cccd_1_.jpg"
file_test=f'/mnt/files/lacvietdemo/2023/12/25/png/6f8f7d47-92a8-413c-94fb-04b5c209797a/2023-12-10_15-01-49.png'
file_test=f'/mnt/files/lacvietdemo/2023/11/24/png/679b2dd4-da27-40fe-b385-359249b15cae/sadsa.png'
file_test=f'/mnt/files/lacvietdemo/2023/11/23/jpg/1666144c-8297-40dc-a10a-beff7bd1eb5b/2.jpg'
file_test=f"/mnt/files/lacvietdemo/2023/11/27/png/c320f1b4-051f-43fb-a759-9058f77534da/5.png"
# file_test=f"/mnt/files/lacvietdemo/2024/01/08/png/094353ad-2717-4d59-a3b3-4bff941cb466/6.png"
file_test=f"/mnt/files/lacvietdemo/2024/01/10/png/659446ab-f316-42fa-9324-e4e1a25ab371/2024-01-09_16-27-56.png"
# file_test=f'/mnt/files/lacvietdemo/2023/09/11/png/3e49132c-e5cd-44ab-82b2-d25a931e78ee/screenshot_96.png'
# file_test=f"/mnt/files/lacvietdemo/2024/01/09/jpg/f6c4f3c4-2d99-401c-a1ec-c155f5911c13/so-bia-cong.jpg"
# # file_test=f"/mnt/files/lv-docs/2023/09/29/png/21830923-6c65-4d38-9025-a7cd2daa6d00/aaa.png"
file_test=f"/mnt/files/lacvietdemo/2024/01/12/jpg/aad020e0-3b99-4236-9c4d-0a2830a088ad/â.jpg"
def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--img', required=True, help='foo help')
    # parser.add_argument('--config', required=True, help='foo help')
    global_angle = get_skew(file_test)
    ret=get_all_rectangles(file_test,f"/mnt/files/dataset/easyocr",f"/mnt/files/cacher")
    # args = parser.parse_args()
    base_config = Cfg.load_config_from_file(f"/home/vmadmin/python/cy-py/cyx/ocr_vietocr_utils/config/base.yml")
    config = Cfg.load_config_from_file(f"/home/vmadmin/python/cy-py/cyx/ocr_vietocr_utils/config/vgg-transformer.yml")
    # config = Cfg.load_config_from_file(f"/home/vmadmin/python/cy-py/cyx/ocr_vietocr_utils/config/vgg-seq2seq.yml")
    config= {**base_config, **config, 'device': 'cpu'}
    detector = Predictor(config)
    img = Image.open(file_test)
    w,h =img.size
    img_array = numpy.array(img)
    ret_contents=[]
    ret_frames=[]
    score=0
    dy=min([max([x[1] for x in fx])-min([x[1] for x in fx]) for fx in ret])
    for i in tqdm(range(len(ret))):
        fx= ret[i]
        x1=min([x[0] for x in fx])
        y1 = min([x[1] for x in fx])
        x2 = max([x[0] for x in fx])
        y2 = max([x[1] for x in fx])

        cropped_image = img_array[y1:y2, x1:x2, ...]
        cropped_im = Image.fromarray(cropped_image)
        rate_scale = cropped_im.height/cropped_im.height



        cropped_im.save(f"/mnt/files/cacher/test_{x1}_{y1}_{x2}_{y2}_cropped.png")
        # angle = get_skew(f"/mnt/files/cacher/test_{x1}_{y1}_{x2}_{y2}.png")
        angle= get_skew(cropped_im) or 0
        # rotate_img = rotate(cropped_im,angle,background=(0,0,0))
        # image_pil = Image.fromarray(rotate_img.astype(numpy.uint8))  # Ensure uint8 type for images
        # image_pil.save(f"/mnt/files/cacher/test_{x1}_{y1}_{x2}_{y2}.png")
        s = detector.predict(cropped_im)

        # rows = math.floor((y1  /math.cos(angle)) / dy)
        # cols = math.floor((x1  /math.cos(angle)) / config["dataset"]["image_min_width"])
        # score = (cols/rate_scale + (rows/rate_scale) * w)
        # score=score/math.cos(angle)
        # s = suggestions.suggest(s)
        ret_contents+=[dict(
            text=s,
            # score=score,
            # rows=rows,
            # cols=cols,
            # x1=x1,
            # x2=x2,
            # y1=y1,
            # y2=y2,
            # center_x=(x1+x2)/2,
            # center_y=(y1+y2)/2,
            # center_score=x1+((y1+y2)/2)*img.width,
            score= math.floor(((y1+y2)/2)/dy)*img.width+math.floor(((x1+x2)/2)/dy),
            score1=math.floor(((x1 + x2) / 2) / dy) * img.height + math.floor(((y1 + y2) / 2) / dy),
            # angle=angle

        )]
        ret_frames+=[(x1,y1),(x2,y2)]
    if global_angle!=0:
        sorted_list = sorted(ret_contents, key=lambda item: item["score1"])
    else:
        sorted_list = sorted(ret_contents, key=lambda item: item["score"])

    txt=" ".join([x["text"] for x in sorted_list])
    for x in sorted_list:
        print(x["text"])
    print(txt)

if __name__ == '__main__':
    main()