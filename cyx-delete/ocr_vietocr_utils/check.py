import math
import os.path

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from cyx.ocr_easy_utils import get_all_rectangles,get_skew,rotate
from cyx.ocr_vietocr_utils import ocr_content
# from PIL import Image
# import PIL.Image
# import numpy
# from tqdm import tqdm
# if not hasattr(Image,"ANTIALIAS"):
#     setattr(Image,"ANTIALIAS",PIL.Image.Resampling.LANCZOS)
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
    txt= ocr_content.ocr_image(file_test)
    print(txt)

if __name__ == '__main__':
    main()