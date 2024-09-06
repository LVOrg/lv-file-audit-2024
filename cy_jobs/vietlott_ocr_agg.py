"""
docker run -it  --entrypoint=/bin/bash -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app nttlong/ocr-my-pdf-api:7
"""
import pathlib
import sys
from icecream import ic
import hashlib
import os
import requests
import typing
from tqdm import tqdm
from PyPDF2 import PdfReader, PdfWriter
from tika import parser


sys.path.append("/app")
from cyx.repository import Repository
import cy_docs
import cy_kit
from cyx.base import config
from cy_xdoc.services.search_engine import SearchEngine
from cyx.local_api_services import LocalAPIService
import img2pdf
import traceback
import fitz
import  shutil
from retry import retry
import  subprocess
sort_rev= False

"""
Declare resource
"""
app_name = "default"

search_engine = cy_kit.singleton(SearchEngine)
local_api_service = cy_kit.singleton(LocalAPIService)

temp_processing_file = os.path.join("/mnt/files", "__lv-files-tmp__")
os.makedirs(temp_processing_file,exist_ok=True)
temp_path = os.path.join(temp_processing_file, "tmp-upload")
ic(f"tem dir for download file is {temp_path}")
ic(app_name)
from cyx.common.mongo_db_services import RepositoryContext
@cy_docs.define(name="ocr-loc")
class OcrLock:
    url: str

ocr_lock = RepositoryContext[OcrLock](OcrLock)
def download_file_with_progress(url, filename)->typing.Tuple[str|None,dict|None]:
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
    directory_of_file = pathlib.Path(filename).parent.__str__()
    os.makedirs(directory_of_file,exist_ok=True)

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

def get_agg(sort_expr:bool,limit:int=10):
    """
    Create an aggregate get all file not OCR yet
    @param sort_expr:
    @return:
    """
    ic(sort_expr)
    sort_expr = Repository.files.fields.RegisterOn.desc() if sort_rev else Repository.files.fields.RegisterOn.asc()

    agg_files = Repository.files.app(app_name).context.aggregate().match(
                Repository.files.fields.FileExt == "pdf"
            ).match(
                Repository.files.fields.Status == 1
            ).match(
                ((Repository.files.fields.IsHasORCContent==False)|
                 (Repository.files.fields.IsHasORCContent=="false")|
                 (Repository.files.fields.IsHasORCContent==None)
                )
            ).sort(
                sort_expr
            ).project(
                cy_docs.fields.upload_id>> Repository.files.fields.id,
                cy_docs.fields.download_url >> Repository.files.fields.FullFileNameLower
            ).limit(limit)
    ic(agg_files)
    return agg_files


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

@retry(tries=10, delay=5)
def check_es_source(app:str,id:str)->bool:
    """
    Check if doc with id in app has content
    @param app:
    @param id:
    @return:
    """
    es_doc_item = search_engine.get_doc(
        app_name=app,
        id=id
    )
    check = (es_doc_item and hasattr(es_doc_item, "source") and
             hasattr(es_doc_item.source, "content") and
             isinstance(es_doc_item.source.content, str) and
             len(es_doc_item.source.content) > 0)
    return  check
def do_ocr_file(x_file:str):
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
            subprocess.run(command)
    except:
        print(traceback.format_exc())
    return page_out_put if os.path.isfile(page_out_put) else None
def concat_content(contents):
    txt_content=" ".join([x for x in contents if x is not None])
    for x in ['\n','\r','\t']:
        txt_content = txt_content.replace(x, " ")
    txt_content = txt_content.rstrip(" ").lstrip(" ")
    while "  " in txt_content:
        txt_content = txt_content.replace("  "," ")
    return txt_content


def get_content(
        tika_server: str ,
        remote_file: str

)->str:
    hash_object = hashlib.sha256(remote_file.encode())
    load_file_name = hash_object.hexdigest()
    process_file = os.path.join(temp_path,f"{load_file_name}-input.pdf")
    process_file = download_file_with_progress(
        url=remote_file, filename=process_file
    )
    if process_file is None:
        # Can not download
        return None
    output_dir = os.path.join(temp_processing_file,load_file_name)
    all_files = extract_files(process_file, output_dir) or {}
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

    shutil.rmtree(output_dir,ignore_errors=True)
    return  txt_content


def do_ocr_content(app_name:str, upload_id:str)->str|None:
    """
    get content by perform OCR
    @param app_name:
    @param upload_id:
    @return:
    """
    upload_item = Repository.files.app(app_name).context.find_one(
        Repository.files.fields.id==upload_id
    )
    if not upload_item:
        return  None
    upload_item = upload_item.to_json_convertable()
    url_file,_,_,_,_ = local_api_service.get_download_path(
        app_name =app_name,
        upload_item =upload_item

    )
    ic(url_file)
    content = get_content(
        tika_server = config.tika_server,
        remote_file=url_file
    )
    ic(content[:100])
@retry(tries=5,delay=10)
def save_es(app_name,upload_id,content):
    search_engine.update_content(
        app_name=app_name,
        id=upload_id,
        content=content,
        replace_content=True
    )
import pymongo.errors
def is_ready(app_name, upload_id):
    try:
        ocr_lock.app(app_name).context.insert_one(
            ocr_lock.fields.id << upload_id

        )
        return False
    except pymongo.errors.DuplicateKeyError:
        return True


def main():

    while True:
        agg_files = get_agg(5)
        for item in agg_files:
            upload_id = item.upload_id
            try:

                if is_ready(app_name=app_name,upload_id=upload_id):
                    continue

                ic(upload_id)
                if check_es_source(app=app_name,id= upload_id):
                    """
                    Update ready content from OCR
                    """
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.id==upload_id,
                        Repository.files.fields.HasORCContent<<True
                    )
                    continue
                content = do_ocr_content(app_name=app_name,upload_id=upload_id)
                save_es(
                    app_name=app_name,
                    upload_id = upload_id,
                    content = content
                )
                ic(f"{upload_id} Update ES is OK")
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id== upload_id,
                    Repository.files.fields.HasORCContent << True
                )
            except:
                ocr_lock.app(app_name).context.delete(
                    ocr_lock.fields.id==upload_id
                )



if __name__ == "__main__":
    main()
#docker run --entrypoint=python3  docker.lacviet.vn/xdoc/fs-ocr-vietlott:latest cy_jobs/vietlott_ocr_agg.py