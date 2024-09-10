"""
docker run -it  --entrypoint=/bin/bash -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app nttlong/ocr-my-pdf-api:7
"""
import pathlib
import sys
import threading
import time

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
import datetime
"""
Declare resource
"""
app_name = "default"
if hasattr(config,"app_name"):
    app_name = config.app_name
search_engine = cy_kit.singleton(SearchEngine)
local_api_service = cy_kit.singleton(LocalAPIService)

temp_processing_file = os.path.join("/tmp/files", "__lv-files-tmp__")
os.makedirs(temp_processing_file,exist_ok=True)
temp_path = os.path.join(temp_processing_file, "tmp-upload")
ic(f"tem dir for download file is {temp_path}")
ic(app_name)

from cyx.logs_to_mongo_db_services import LogsToMongoDbService
logs_to_mongo_db_service =cy_kit.singleton(LogsToMongoDbService)
sort_rev= False
if hasattr(config,"recent"):
    sort_rev = config.recent
from cyx.common.mongo_db_services import RepositoryContext
@cy_docs.define(name="ocr-loc")
class OcrLock:
    url: str
    pod_name:str

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

def get_agg(list_ids,sort_expr:bool,limit:int=10,skip=10):
    """
    Create an aggregate get all file not OCR yet
    @param sort_expr:
    @return:
    """
    # ic(sort_expr)

    sort_expr = Repository.files.fields.RegisterOn.desc() # if sort_rev else Repository.files.fields.RegisterOn.asc()

    agg_files = Repository.files.app(app_name).context.aggregate().match(
                Repository.files.fields.FileExt == "pdf"
            ).match(
                Repository.files.fields.Status == 1
            ).match(
                ((Repository.files.fields.IsHasORCContent==False)|
                 (Repository.files.fields.IsHasORCContent=="false")|
                 (Repository.files.fields.IsHasORCContent==None)
                )
            ).match(
                    {"_id": { "$nin": list_ids }}
            ).sort(
                sort_expr
            ).project(
                cy_docs.fields.upload_id>> Repository.files.fields.id,
                cy_docs.fields.download_url >> Repository.files.fields.FullFileNameLower
            ).skip(skip).limit(limit)
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
        raise

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
    try:
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
    except:
        ocr_file = do_ocr_file(process_file)
        if ocr_file:
            parsed_data = parser.from_file(ocr_file, serverEndpoint=tika_server)
            contents = [parsed_data.get("content", "")]
            txt_content = concat_content(contents)
            return txt_content


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
    return content
@retry(tries=5,delay=10)
def save_es(app_name,upload_id,content):
    search_engine.update_content(
        app_name=app_name,
        id=upload_id,
        content=content,
        replace_content=True
    )
import pymongo.errors

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
def is_ready(app_name, upload_id,pod_name:str):
    try:
        ocr_lock.app(app_name).context.insert_one(
            ocr_lock.fields.id << upload_id,
            ocr_lock.fields.pod_name <<pod_name

        )
        return None
    except pymongo.errors.DuplicateKeyError:
        ret = ocr_lock.app(app_name).context.find_one(
            ocr_lock.fields.id == upload_id

        )
        if ret:
            return ret[ocr_lock.fields.pod_name]
        else:
            return None

def update_HasORCContent():
    lst = list(get_agg([],True,100))
    while len(lst)>0:
        for x in lst:
            if check_es_source(app=app_name,id= x.id):
                """
                Update ready content from OCR
                """
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id==x.id,
                    Repository.files.fields.HasORCContent<<True
                )
        lst = list(get_agg([], True, 100))


def main():
    skip=0
    while True:
        # list_ids_doc = ocr_lock.app(app_name).context.aggregate().project(
        #     cy_docs.fields.upload_id>>ocr_lock.fields.id
        # )
        # list_ids = [x.upload_id for x in list_ids_doc]
        # if len(list_ids)>32: #32 pod
        #     for x in list_ids:
        #         ocr_lock.app(app_name).context.delete(
        #             {}
        #         )
        #     list_ids = []
        list_ids = []
        agg_files = get_agg([],True)
        for item in agg_files:
            upload_id = item.upload_id
            try:

                # if pod_process:=is_ready(app_name=app_name,upload_id=upload_id,pod_name=get_pod_name()):
                #     ic(f"{upload_id} read by {pod_process}")
                #     continue

                ic(upload_id)
                # if check_es_source(app=app_name,id= upload_id):
                #     """
                #     Update ready content from OCR
                #     """
                #     Repository.files.app(app_name).context.update(
                #         Repository.files.fields.id==upload_id,
                #         Repository.files.fields.HasORCContent<<True
                #     )
                #     continue
                content = do_ocr_content(app_name=app_name,upload_id=upload_id)
                upload_data_item = Repository.files.app(app_name).context.find_one(
                    Repository.files.fields.id==upload_id
                )
                if search_engine.is_exist(app_name=app_name,id=upload_id):
                    search_engine.update_content_value_only(
                        app_name=app_name,
                        id= upload_id,
                        content=content,
                        content_lower=content.lower()
                    )
                else:
                    search_engine.make_index_content(
                        app_name=app_name,
                        upload_id=upload_id,
                        data_item=upload_data_item.to_json_convertable(),
                        privileges=upload_data_item[Repository.files.fields.Privileges],
                        content=content

                    )
                if not check_es_source(app=app_name,id=upload_id):
                    raise Exception("Cannot update ES")
                ic(f"{upload_id} Update ES is OK")
                Repository.files.app(app_name).context.update(
                    Repository.files.fields.id== upload_id,
                    Repository.files.fields.HasORCContent << True
                )
                Repository.lv_file_content_process_report.app("admin").context.insert_one(
                    Repository.lv_file_content_process_report.fields.UploadId << upload_id,
                    Repository.lv_file_content_process_report.fields.SubmitOn << datetime.datetime.utcnow()
                )

            except:

                Repository.lv_files_sys_logs.app("admin").context.insert_one(
                    Repository.lv_files_sys_logs.fields.LogOn << datetime.datetime.utcnow(),
                    Repository.lv_files_sys_logs.fields.ErrorContent << traceback.format_exc(),
                    Repository.lv_files_sys_logs.fields.PodId << get_pod_name(),
                    Repository.lv_files_sys_logs.fields.Url << upload_id,
                    Repository.lv_files_sys_logs.fields.WorkerIP << get_pod_name()
                )



if __name__ == "__main__":
    # threading.Thread(target=update_HasORCContent).start()
    main()
#docker run --entrypoint=python3  docker.lacviet.vn/xdoc/fs-ocr-vietlott:build-22.2024-9-06-17-31-11 cy_jobs/vietlott_ocr_agg.py recent=true app_name=developer
#docker run -it --entrypoint=/bin/bash -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app docker.lacviet.vn/xdoc/fs-ocr-vietlott:build-22.2024-9-06-13-59-38
#python /app/cy_jobs/vietlott_ocr_agg.py app_name=developer
#docker run --entrypoint=/bin/bash -it -v -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app docker.lacviet.vn/xdoc/lib-ocr