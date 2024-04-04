import pathlib
import shutil
import sys
import typing
import uuid

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cy_file_cryptor.wrappers
import cyx.framewwork_configs

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo

from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common import config

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cyx.common.mongo_db_services import MongodbService
from cyx.local_api_services import LocalAPIService
from cyx.socat_services import SocatClientService
import os

__check_id__ = {}

import fitz
from PIL import Image


def vertical_append(images_list: typing.List[str], out_put: str) -> str:
    images = []
    for image_path in images_list:
        images.append(Image.open(image_path))
    if len(images) == 0:
        return None
    total_height = sum(img.height for img in images)
    max_width = -1
    try:
        max_width = max(img.width for img in images)
    except Exception as e:
        return None

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
        image_path = os.path.join(extract_to, f"page_{page_index:04d}.png")
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
        if len(image_paths) == 0:
            return None
        vertical_append(image_paths, image_path)
        ret += [image_path]
        page_index += 1
    return ret


@broker(message=cyx.common.msg.MSG_FILE_EXTRACT_IMAGES_FROM_PDF)
class Process:
    def __init__(self,
                 mongodb_service=cy_kit.singleton(MongodbService),
                 logger=cy_kit.singleton(LoggerService),
                 local_api_service=cy_kit.singleton(LocalAPIService),
                 socat_client_service = cy_kit.singleton(SocatClientService)
                 ):
        self.logger = logger
        self.mongodb_service = mongodb_service
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.temp_dir = "/tmp-files"
        self.local_api_service = local_api_service
        self.socat_client_service = socat_client_service
        self.socat_client_service.start(3456)

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        rel_file_path = msg_info.Data["MainFileId"].split("://")[1]
        local_share_id = None
        token = None
        server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
        if not msg_info.Data.get("local_share_id"):
            token = self.local_api_service.get_access_token("admin/root", "root")
            server_file += f"?token={token}"
        else:
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
        download_file = os.path.join(self.temp_dir, str(uuid.uuid4()))
        with open(server_file, "rb") as fs:
            with open(download_file, "wb") as fd:
                fd.write(fs.read())
        out_put_dir_name = str(uuid.uuid4())
        out_put_dir = os.path.join(self.temp_dir,out_put_dir_name)
        os.makedirs(out_put_dir,exist_ok=True)
        image_files = extract_all_images(download_file,out_put_dir)
        search_content_file = f"{rel_file_path}.images.search.es"
        result_file = f"{download_file}.txt"
        print(f"Ssave file {result_file} to {search_content_file} ...")
        for x in image_files:
            ocr_command = f"python3.9 /cmd/ocr.py {x}"
            ret = self.socat_client_service.send(ocr_command)
            txt_file= f"{x}.txt"
            if os.path.isfile(txt_file):
                with open(txt_file,"rb") as fs:
                    if not os.path.isfile(result_file):
                        with open(result_file,"wb") as fw:
                            fw.write(fs.read()+" ".encode())
                    else:
                        with open(result_file,"ab") as fw:
                            fw.write(fs.read()+" ".encode())




            self.local_api_service.send_file(
                file_path = result_file,
                token=token,
                local_share_id=local_share_id,
                app_name=msg_info.AppName,
                rel_server_path=search_content_file

            )
            msg.emit_child_message(
                parent_message=msg_info,
                message_type=cyx.common.msg.MSG_FILE_SAVE_SEARCH_CONTENT,
                resource=search_content_file
            )

            print(f"Save file {result_file} to {search_content_file} is ok")

    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
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
                if ret is None:
                    msg.delete(msg_info)
                    return
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

            msg.delete(msg_info)
