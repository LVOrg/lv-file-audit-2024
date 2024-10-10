import pathlib
import shutil
import sys
import time
import traceback

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
import typing

import cy_docs


from cy_jobs.jobs.scaner_db.scaners import Scaner, ScanEntity
from cyx.common import config
from cyx.db_models.files import DocUploadRegister
from cyx.repository import Repository
from cy_kit.design_pattern import singleton
from icecream import ic
import os
import PyPDF2
import cy_file_cryptor.context
import cy_file_cryptor.wrappers
from PIL import Image
from PyPDF2 import PdfReader
import PyPDF2.generic._base
import PyPDF2.generic._data_structures
import PIL
import io
import fitz
from retry import retry
import requests
from tika import  parser as tika_parser
cy_file_cryptor.context.set_server_cache(config.cache_server)
class PdfPageItemInfo:
    image_files: typing.List[str]
    file_name: str
class PdfPageInfo:
    main_file:str
    pages: typing.List[PdfPageItemInfo]
    dir_path: str
    """
    Director of temp folder
    """

from elasticsearch import Elasticsearch
from  cy_es import cy_es_manager
@singleton()
class OCR:
    scaner_files:Scaner[DocUploadRegister] = None
    def __init__(self):
        self.scaner_files=Scaner[DocUploadRegister](
            DocUploadRegister,
            Repository.files,
            app_name=config.app_name,
            scan_value=config.version,
            scan_id= type(self).__name__ )
        self.scaner_files.filter = self.scaner_files.filter & (
            (self.scaner_files.F.Status>0)&(self.scaner_files.F.FileExt=="pdf")
        )
        self.temp_dir = os.path.join(config.file_storage_path,"--tmp--")
        os.makedirs(self.temp_dir,exist_ok=True)
        self.ocr_url = config.ocr_url
        self.es_client = Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=120,
            sniff_timeout=30
        )
        self.prefix_index = config.elastic_search.prefix_index
        while not self.heal_check_remote_server():
            ic(f"Check {self.ocr_url}/swagger/index.html was fail, try next 5 second")
            time.sleep(5)
        ic(f"Check {self.ocr_url}/swagger/index.html is OK")

    def heal_check_remote_server(self)->bool:
        try:
            response = requests.get(self.ocr_url+"/swagger/index.html")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            return False
    def upload_file_and_get_ocr_result(self,file_path):
        """Uploads a file to the specified endpoint and retrieves the OCR result.

        Args:
            file_path (str): The path to the file to be uploaded.

        Returns:
            dict: The OCR result as a JSON object.
        """

        url = self.ocr_url+ "/Document/get-ocr-result"

        # Prepare the file for upload
        with open(file_path, 'rb') as file:
            files = {'file': file}

        # Send the POST request with the file
            response = requests.post(url, files=files)
            response.raise_for_status()

            # Check the response status code
            if response.status_code == 200:
                # Parse the JSON response
                ocr_result = response.json()
                if ocr_result.get('Succeeded'):
                    ret_txt: str = (ocr_result.get('Data') or {}).get('Content')
                    ret_txt = ret_txt.replace('\r',' ')
                    ret_txt = ret_txt.replace('\n', ' ')
                    ret_txt = ret_txt.replace('\t', ' ')
                    while '  ' in ret_txt:
                        ret_txt = ret_txt.replace('  ',' ')
                    ret_txt  =  ret_txt.lstrip(' ').rstrip(' ')
                    return ret_txt
                else:
                    try:
                        json_res = response.json()
                        if json_res.get("Succeeded")==False and json_res.get("Content") =="":
                            return ""
                        elif json_res.get("Succeeded")==False and json_res.get("Message"):
                            raise Exception(json_res.get("Message"))
                    except:
                        raise Exception(response.text)
            else:
                raise Exception("Error uploading file: " + response.text)
    def get_upload_data(self,entity:ScanEntity):
        upload = entity.context.find_one(
            cy_docs.fields._id==entity.entity_id
        )
        return upload
    def do_ocr(self,*sort):
        for x in self.scaner_files.get_entities(*sort):
            upload_item = self.get_upload_data(x)
            if not upload_item:
                x.commit()
                continue
            main_file_id = upload_item.get(self.scaner_files.F.MainFileId.__name__)
            if not isinstance(main_file_id,str):
                x.commit()
                continue
            if not "://" in main_file_id:
                x.commit()
                continue
            file_path = os.path.join(config.file_storage_path.replace('/',os.sep),main_file_id.split("://")[1])
            if not os.path.isfile(file_path):
                x.commit()
                continue
            content=None
            try:
                decrypt_file = self.decrypt_file(file_path)
                content = self.get_ocr_content(decrypt_file)
                decrypt_dir = pathlib.Path(decrypt_file).parent.__str__()
                ic(f"red content was finis, delete dir {decrypt_dir}")
                shutil.rmtree(decrypt_dir,ignore_errors=True)
            except:
                x.error(
                    error_content=traceback.format_exc()
                )
                continue
            es_index = f"{self.prefix_index}_{x.app_name}"
            @retry(tries=10,delay=10)
            def run_update_es():
                cy_es_manager.update_or_insert_content(
                    client = self.es_client,
                    index = es_index,
                    id = upload_item.id,
                    content = content
                )
                update_doc = {
                    "doc": {
                        "data_item": {
                            "Status":1
                        }
                    }
                }
                ret = self.es_client.update(index=es_index, id=upload_item.id, body=update_doc, doc_type="_doc")
                return ret
            run_update_es()
            x.commit()


    def get_pixmaps_in_pdf(self,pdf_filename):
        doc = fitz.open(pdf_filename)
        xrefs = set()
        for page_index in range(doc.page_count):
            for image in doc.get_page_images(page_index):
                xrefs.add(image[0])  # Add XREFs to set so duplicates are ignored
        pixmaps = [fitz.Pixmap(doc, xref) for xref in xrefs]
        doc.close()
        return pixmaps
    def raw_extract_images(self,infile_name):
        not_found_any_image = True
        try:
            with open(infile_name, 'rb') as in_f:
                in_pdf = PdfReader(in_f,strict=True)
                ic(f"{len(in_pdf.pages)} page found in {infile_name}")

                for page_no in range(len(in_pdf.pages)):
                    page = in_pdf.pages[page_no]
                    if len(page.images)==0:
                        break
                    not_found_any_image= False
                    for image in page.images:
                        img = PIL.Image.open(io.BytesIO(image.data))
                        yield img
            if not_found_any_image:
                pixmaps = self.get_pixmaps_in_pdf(infile_name)
                for pixmap in pixmaps:
                    yield pixmap
        except NotImplementedError:
            for x in self.get_pixmaps_in_pdf(infile_name):
                yield x
        except PyPDF2.errors.PdfReadError:
            for x in self.get_pixmaps_in_pdf(infile_name):
                yield x
        except OSError:
            for x in self.get_pixmaps_in_pdf(infile_name):
                yield x
        except ValueError:
            for x in self.get_pixmaps_in_pdf(infile_name):
                yield x
        except UnboundLocalError:
            for x in self.get_pixmaps_in_pdf(infile_name):
                yield x
    def decrypt_file(self,file_path:str)->str:
        rel_file_name = file_path[len(config.file_storage_path) + 1:]
        tem_file_path = os.path.join(self.temp_dir, rel_file_name)
        tmp_dir_path = pathlib.Path(tem_file_path).parent.__str__()
        os.makedirs(tmp_dir_path, exist_ok=True)
        with open(file_path, "rb") as fr:
            with open(tem_file_path, "wb") as fw:
                fw.write(fr.read())
        return tem_file_path
    def get_pdf_pages(self, decrypt_file_path:str)->typing.Iterable[PdfPageInfo]:
        ret = PdfPageInfo()
        tmp_dir_path = pathlib.Path(decrypt_file_path).parent.__str__()
        ret.main_file = decrypt_file_path
        ret.pages=[]
        with open(decrypt_file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            for page_num in range(num_pages):
                page_item_info = PdfPageItemInfo()
                page_item_info.image_files = []
                pdf_writer = PyPDF2.PdfWriter()
                page = pdf_reader.pages[page_num]
                if page.annotations:
                    page.annotations.clear()
                pdf_writer.add_page(page)
                output_pdf_path = os.path.join(tmp_dir_path,f"page_{page_num}.pdf")
                with open(output_pdf_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                page_item_info.file_name = output_pdf_path
                raw_images = self.raw_extract_images(output_pdf_path)
                i = 0
                for img in raw_images:
                    image_file_name = f"image_{page_num}_{i}_.png"
                    image_file_path = os.path.join(tmp_dir_path, image_file_name)
                    if hasattr(img, "writePNG") and callable(img.writePNG):
                        img.writePNG(image_file_path)
                        page_item_info.image_files.append(image_file_path)
                    else:
                        img.save(image_file_path, 'png')
                        page_item_info.image_files.append(image_file_path)
                    i += 1

                ret.pages.append(page_item_info)
        ret.dir_path = tmp_dir_path
        yield ret

    def get_content_from_tika(self, file_path):
        @retry(exceptions=(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError), delay=15, tries=10)
        def runing():
            parsed_data = tika_parser.from_file(file_path,
                                               serverEndpoint=config.tika_server,
                                               xmlContent=False,
                                               requestOptions={'timeout': 5000})

            content = parsed_data.get("content", "") or ""
            content = content.lstrip('\n').rstrip('\n').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            while "  " in content:
                content = content.replace("  ", " ")
            content = content.rstrip(' ').lstrip(' ')
            return content

        return runing()

    def get_ocr_content(self,file_path:str):
        contents= []
        for pdf_info in self.get_pdf_pages(file_path):
            for page_item in pdf_info.pages:
                if page_item.file_name and os.path.isfile(page_item.file_name):
                    tika_content = self.get_content_from_tika(page_item.file_name)
                    contents.append(tika_content)
                    ic(tika_content[0:20])
                    for image_path in page_item.image_files:
                        net_ocr_content = self.upload_file_and_get_ocr_result(image_path)
                        contents.append(net_ocr_content)
                        ic(net_ocr_content[0:20])
        return " ".join(contents)


def main():
    runner = OCR()
    runner.do_ocr(runner.scaner_files.F.RegisterOn.desc())
if __name__ == "__main__":
    main()
# python cy_jobs/jobs/task_saas_ocr_recent.py app_name=all version=ocr-003 ocr_url=http://localhost:5000