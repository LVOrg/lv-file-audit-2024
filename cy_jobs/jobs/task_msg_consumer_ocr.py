import os.path
import sys
import pathlib
import traceback



sys.path.append("/app")
sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
import pika.exceptions
import cy_kit

from cyx.repository import Repository
from icecream import ic
from tqdm import tqdm
from cyx.common import config
import requests
if not hasattr(config, "msg_ocr"):
    raise Exception(f"msg_ocr was not found in config")
if not hasattr(config, "app_name"):
    raise Exception(f"app_name was not found in config")
msg_raise_ocr: str = config.msg_ocr
"""
Message wil be raise 
"""
app_name: str = config.app_name
ic(f"app_name={app_name}, msg_ocr={msg_raise_ocr}")
from cyx.rabbit_utils import Consumer, MesssageBlock
from cyx.local_api_services import LocalAPIService
local_api_service = cy_kit.single(LocalAPIService)
import hashlib
from PyPDF2 import PdfReader, PdfWriter
import shutil
import img2pdf
import fitz
import subprocess
from tika import parser
temp_ocr_file_dir_name="__temp_ocr_file__"
from cyx.common.mongo_db_services import RepositoryContext
import pymongo.errors
import cy_docs
@cy_docs.define(name=f"log-ocr-{msg_raise_ocr}",uniques=["upload_id"])
class OcrLogs:
    upload_id:str
    content_path:str
    pod_name:str
    is_error:bool
    error_conent:str
    app_name:str

ocr_logs = RepositoryContext[OcrLogs](OcrLogs)
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service =cy_kit.singleton(LogsToMongoDbService)
def extract_files(pdf_path, output_dir) -> dict:
    """Extracts images from a PDF file and saves them to an output directory.

  Args:
    pdf_path: Path to the PDF file.
    output_dir: Directory to save extracted images.
  """
    os.makedirs(output_dir,exist_ok=True)
    ret = {}
    reader = PdfReader(open(pdf_path, 'rb'))
    num_pages = len(reader.pages)

    for page_num in range(num_pages):
        page = reader.pages[page_num]
        output_filename = os.path.join(output_dir, f"{page_num}-split.pdf")
        writer = PdfWriter()
        writer.add_page(page)
        writer.write(open(output_filename, 'wb'))

        ret[output_filename] = dict()
    for split_page in list(ret.keys()):
        doc = fitz.open(split_page)
        page = doc[0]
        ret[split_page]["images"] = []
        ret[split_page]["pdf_from_images"] = []
        img_id =0
        for img in page.get_images():
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            # Save image to output directory
            output_path = f"{split_page}_{img_id}_{xref}.{ext}"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
                ret[split_page]["images"] += [output_path]
            with open(f"{output_path}.pdf", "wb") as f:
              f.write(img2pdf.convert([output_path]))
            ret[split_page]["pdf_from_images"]+=[f"{output_path}.pdf"]
            img_id+=1
    return ret

def concat_content(contents):
    txt_content=" ".join([x for x in contents if x is not None])
    for x in ['\n','\r','\t']:
        txt_content = txt_content.replace(x, " ")
    txt_content = txt_content.rstrip(" ").lstrip(" ")
    while "  " in txt_content:
        txt_content = txt_content.replace("  "," ")
    return txt_content


class OCRError(Exception):
    """Custom exception class for OCR-related errors."""

    def __init__(self, msg):
        """Initializes the OCRError instance.

        Args:
            msg (str): The error message.
        """

        super().__init__(msg)



def do_ocr_file(x_file:str,force_ocr=False):
    """
    Exception OCRError
    @param x_file:
    @param force_ocr:

    @return:
    """
    page_out_put=f"{x_file}-ocr.pdf"

    try:
            command = ["ocrmypdf",
                           "-l", "vie",
                           "--rotate-pages",
                           "--deskew",
                           # "--skip-text",
                           # "--redo-ocr",
                           # "--force-ocr",
                           # "--title", "My PDF",
                           "--jobs", "2",
                           "--output-type", "pdfa",
                           # "--tesseract - timeout", "300",
                           x_file,
                           page_out_put]
            print(" ".join(command))
            subprocess.run(command)
    except:
        command = ["ocrmypdf",
                   "-l", "vie",
                   "--rotate-pages",
                   "--deskew",
                   # "--skip-text",
                   # "--redo-ocr",
                   "--force-ocr",
                   # "--title", "My PDF",
                   "--jobs", "2",
                   "--output-type", "pdfa",
                   # "--tesseract - timeout", "300",
                   x_file,
                   page_out_put]
        print(" ".join(command))
        subprocess.run(command)
    if not os.path.isfile(page_out_put):
        raise OCRError(f"Ca not ORC File{x_file}")
    return page_out_put if os.path.isfile(page_out_put) else None
def get_content(
        tika_server: str ,
        pfd_file_path: str

)->str:
    """
    Exception OCRError
    @param tika_server:
    @param pfd_file_path:
    @return:
    """
    file_name = f"{pathlib.Path(pfd_file_path).stem}-processing"
    output_dir = os.path.join(pathlib.Path(pfd_file_path).parent.__str__(),file_name)
    os.makedirs(output_dir)
    try:
        all_files = extract_files(pfd_file_path, output_dir) or {}
        contents = []
        for file in all_files.keys():
            parsed_data = parser.from_file(file, serverEndpoint=tika_server)
            contents += [parsed_data.get("content", "")]
            for x_file in all_files[file].get("pdf_from_images") or []:
                print(x_file)
                ocr_file= do_ocr_file(x_file)
                if ocr_file:
                    parsed_data = parser.from_file(ocr_file, serverEndpoint=tika_server)
                    contents += [parsed_data.get("content", "")]
        txt_content = concat_content(contents)


        return  txt_content
    except:
        ocr_file = do_ocr_file(pfd_file_path)
        if ocr_file:
            parsed_data = parser.from_file(ocr_file, serverEndpoint=tika_server)
            contents = [parsed_data.get("content", "")]
            txt_content = concat_content(contents)
            return txt_content

def download_file_with_progress(url, filename):
  """
  Downloads a file from the given URL with a progress bar.

  Args:
      url (str): URL of the file to download.
      filename (str): Name of the file to save locally.

  Raises:
      Exception: If an error occurs during download.
  """

  # Create response object

  response = requests.get(url, stream=True,verify=False)

  # Check for successful response
  if response.status_code >= 200  and response.status_code<300:
    # Get file size
    total_size = int(response.headers.get('content-length', 0))

    # Create progress bar
    progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=filename)
    with open(filename, 'wb') as file:
      for data in response.iter_content(chunk_size=1024):
        progress_bar.update(len(data))
        file.write(data)

    progress_bar.close()
    ic(f"File '{filename}' downloaded was successfully.")
    return filename
  else:
    ic(f"File '{filename}' downloaded was fail.")
    return None


def do_hash_content_256_file(file_path:str):
    """Calculates the SHA-256 hash of a file's content.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The SHA-256 hash of the file's content in hexadecimal format.
    """

    if not os.path.exists(file_path):
        return None

    with open(file_path, 'rb') as f:
        content = f.read()
        sha256_hash = hashlib.sha256(content).hexdigest()
        return sha256_hash


def do_copy_txt_file(from_file, to_file):
    """Copies a text file from one location to another.

    Args:
        from_file (str): The path to the source file.
        to_file (str): The path to the destination file.
    """

    try:
        dest_dit = pathlib.Path(to_file).parent.__str__()
        os.makedirs(dest_dit,exist_ok=True)
        shutil.copy(from_file, to_file)
        ic(f"File copied successfully from {from_file} to {to_file}")
    except Exception as e:
        print(traceback.format_exc())


def do_write_content_to_txt_file(content, file_path):
    """Writes the given content to a text file.

    Args:
        content (str): The content to be written.
        file_path (str): The path to the output file.
    """

    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Content written successfully to {file_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")


def do_ocr_and_save_to_file(consumer:Consumer, msg:MesssageBlock, save_to_file:str)->str|None:
    """
    Exception OCRError
    @param consumer:
    @param msg:
    @param save_to_file:
    @return:
    """
    app_name = msg.app_name
    url_file, _, _, _, _ = local_api_service.get_download_path(
        app_name=app_name,
        upload_item=msg.data

    )
    ic(url_file)

    tmp_dir_download_file = os.path.join(config.file_storage_path,temp_ocr_file_dir_name,"__tmp_download__").replace('/',os.sep)

    os.makedirs(tmp_dir_download_file,exist_ok=True)
    file_name = hashlib.sha256(url_file.encode()).hexdigest()
    file_download =os.path.join(tmp_dir_download_file,file_name)
    ic(f"file_download={file_download}")
    if not os.path.isfile(file_download):
        ic(f"Not found file={file_download}")
        ic(f"do download {file_download} from {url_file}")
        file_download = download_file_with_progress(url_file,file_download)

    if not file_download:
        ic(f"download file fail url ={url_file}")
        return None
    else:
        ic(f"download file is OK url ={url_file}")
    hash_256_content = do_hash_content_256_file(file_path=file_download)
    hash_256_content_file = os.path.join(tmp_dir_download_file,f'{hash_256_content}.txt')
    content_ocr_file = os.path.join(config.file_storage_path,temp_ocr_file_dir_name,app_name,f'{msg.data.get("_id")}.txt')
    if os.path.isfile(hash_256_content_file):
        ic(f"already content of {url_file}")
        ic(f"copy content from {hash_256_content_file} to {content_ocr_file}")
        do_copy_txt_file(from_file=hash_256_content_file,to_file=content_ocr_file)
        return content_ocr_file

    content = get_content(
        tika_server=config.tika_server,
        pfd_file_path=file_download
    )
    ic(content[:100])
    do_write_content_to_txt_file(content=content,file_path=hash_256_content_file)

    if os.path.isfile(hash_256_content_file):
        ic(f"already content of {url_file}")
        ic(f"copy content from {hash_256_content_file} to {content_ocr_file}")
        do_copy_txt_file(from_file=hash_256_content_file,to_file=content_ocr_file)
        return content_ocr_file


def get_pod_name():
    if sys.platform in ["win32","win64"]:
        import platform
        return platform.node()
    else:
        f = open('/etc/hostname')
        pod_name = f.read()
        f.close()
        full_pod_name = pod_name.lstrip('\n').rstrip('\n')
        return full_pod_name


def consume_msg(consumer: Consumer):
    """
    Do consume message and save ocr result in to file at directory
    @param consumer:
    @param directory:
    @return:
    """
    msg = consumer.get_msg(delete_after_get=False)
    consumer.channel.basic_ack(msg.method.delivery_tag)
    if msg.data is None:
        return
    # xac nhan lai xem upload na da bi xoa hay chua
    upload_id = msg.data.get("_id")
    upload_item = Repository.files.app(
        app_name=msg.app_name
    ).context.find_one(
        Repository.files.fields.id == upload_id
    )
    if upload_item is None:
        ic(f"upload with id={upload_id} was not found")
        return
    else:
        ic(f"upload with id={upload_id} was found")
    try:
        save_to_file = os.path.join(config.file_storage_path,temp_ocr_file_dir_name,app_name,upload_id+".txt").replace('/',os.sep)
        save_to_dir = pathlib.Path(save_to_file).parent.__str__()
        os.makedirs(save_to_dir,exist_ok=True)
        ic(f"do_ocr_and_save_to_file(consumer, {msg,save_to_file})")
        ret_file = do_ocr_and_save_to_file(consumer, msg,save_to_file)
        try:
            ocr_logs.app(app_name).context.insert_one(
                ocr_logs.fields.upload_id<<upload_id,
                ocr_logs.fields.content_path<<ret_file,
                ocr_logs.fields.is_error <<False,
                ocr_logs.fields.pod_name << get_pod_name(),
                ocr_logs.fields.app_name << app_name

            )
        except pymongo.errors.DuplicateKeyError:
            ocr_logs.app(app_name).context.update(
                ocr_logs.fields.upload_id == upload_id,
                ocr_logs.fields.content_path << ret_file,
                ocr_logs.fields.is_error << False,
                ocr_logs.fields.pod_name << get_pod_name(),
                ocr_logs.fields.app_name << app_name
            )

    except:
        consumer.resume(msg)
        try:
            ocr_logs.app(app_name).context.insert_one(
                ocr_logs.fields.upload_id<<upload_id,
                ocr_logs.fields.is_error <<True,
                ocr_logs.fields.error_conent <<traceback.format_exc(),
                ocr_logs.fields.pod_name << get_pod_name(),
                ocr_logs.fields.app_name << app_name
            )
        except pymongo.errors.DuplicateKeyError:
            ocr_logs.app(app_name).context.update(
                ocr_logs.fields.upload_id == upload_id,

                ocr_logs.fields.is_error << True,
                ocr_logs.fields.error_conent <<traceback.format_exc(),
                ocr_logs.fields.pod_name << get_pod_name(),
                ocr_logs.fields.app_name << app_name
            )
        raise

def main():
    consumer = Consumer(msg_type=msg_raise_ocr)
    while True:
        try:
            consume_msg(consumer)
        except pika.exceptions.StreamLostError:
            continue
        except:
            print(traceback.format_exc())
            logs_to_mongo_db_service.log(
                error_content=traceback.format_exc(),
                url=f"consumer {msg_raise_ocr}"
            )

if __name__ == "__main__":
    main()