import pathlib
import shutil
import sys
import typing

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cyx.framewwork_configs
import fitz
from PIL import Image

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common import config
from cyx.common.rabitmq_message import RabitmqMsg

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService, ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.media.contents import ContentsServices
from cyx.content_services import ContentService, ContentTypeEnum
# https://github.com/pbcquoc/vietocr/blob/master/vietocr/predict.py
import os

__check_id__ = {}

from cyx.easy_ocr import EasyOCRService
from cy_xdoc.services.search_engine import SearchEngine


def vertical_append(images_list: typing.List[str], out_put: str) -> str:
    images = []
    for image_path in images_list:
        images.append(Image.open(image_path))
    total_height = sum(img.height for img in images)
    max_width = max(img.width for img in images)
    new_image = Image.new("RGB", (max_width, total_height))
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height
    new_image.save(out_put)
    return out_put
def extract_all_images(pdf_file, extract_to) -> typing.List[str]:
    doc = fitz.open(pdf_file)

    ret = []
    num_of_pages = len(doc)
    print(f"Process {num_of_pages} pages in {pdf_file}")
    for page_index in range(0, num_of_pages):
        page = doc[page_index]
        image_list = page.get_images()
        # Access the first page (index starts from 0)
        image_index = 0
        image_path = os.path.join(extract_to,f"page_{page_index:04d}.png")
        image_paths = []
        for img in image_list:

            try:
                xref = img[0]  # XREF of the image object
                pix = fitz.Pixmap(doc, xref)  # Get the image as a Pixmap object
                image_bytes = None
                try:
                    image_bytes = pix.tobytes()  # Raw image data
                except:
                    new_pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_bytes = new_pix.tobytes()

                    # Do something with the image data, such as saving it to a file:
                if not os.path.isdir(extract_to):
                    os.makedirs(extract_to, exist_ok=True)
                output_image = os.path.join(extract_to, f"image_{page_index}_{image_index}.png")

                with open(output_image, "wb") as f:
                    f.write(image_bytes)
                img = Image.open(output_image)
                rotated_img = img.rotate(-1 * page.rotation, expand=True)
                rotated_img.save(output_image)
                image_paths += [output_image]

            except  Exception as e:
                print(e)
                pass
            image_index += 1
        vertical_append(image_paths,image_path)
        ret+=[image_path]
        page_index += 1
    return ret


@broker(message=cyx.common.msg.MSG_FILE_OCR_CONTENT_FROM_PDF)
class Process:
    def __init__(self,
                 file_services=cy_kit.singleton(FileServices),
                 content_service=cy_kit.singleton(ContentService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 extract_text_service=cy_kit.singleton(ContentsServices),
                 logger=cy_kit.singleton(LoggerService),
                 easy_ocr_service=cy_kit.singleton(EasyOCRService),
                 search_engine: SearchEngine = cy_kit.singleton(SearchEngine)
                 ):
        self.file_services = file_services
        self.extract_text_service = extract_text_service
        self.content_service = content_service
        self.logger = logger
        self.mongodb_service = mongodb_service
        self.easy_ocr_service = easy_ocr_service
        self.search_engine = search_engine

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        resource = self.content_service.get_master_resource(msg_info)
        print(msg_info)
        print("-------------------------------")
        print(resource)
        if os.path.isfile(resource):
            content_images_dir_path = os.path.join(pathlib.Path(resource).parent.__str__(), "pdf_images")
            ocr_content_dir = os.path.join(pathlib.Path(resource).parent.__str__(), "content_ocr")

            ocr_content_file = os.path.join(ocr_content_dir, "content.txt")
            contents = ""
            if not os.path.isfile(ocr_content_file):
                if not os.path.isfile(ocr_content_dir):
                    os.makedirs(ocr_content_dir, exist_ok=True)
                if not os.path.isdir(content_images_dir_path):
                    os.makedirs(content_images_dir_path)
                ret = extract_all_images(pdf_file=resource, extract_to=content_images_dir_path)
                full_text = ""
                for file in ret:
                    text = self.easy_ocr_service.get_text(file)
                    full_text += text + " "
                contents = self.content_service.well_form_text(full_text)
                with open(ocr_content_file, "wb") as fs:
                    fs.write(contents.encode('utf8'))

                print(ret)
            else:
                with open(ocr_content_file, "rb") as fs:
                    contents = fs.read().decode("utf8")
            ret_source = self.search_engine.get_source(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"]
            )
            self.search_engine.replace_content(
                app_name=msg_info.AppName,
                id=msg_info.Data["_id"],
                field_path="content_ocr",
                field_value=contents
            )

            # msg.delete(msg_info)
