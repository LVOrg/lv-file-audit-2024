import pathlib
import sys
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
cy_file_cryptor.context.set_server_cache(config.cache_server)
class PdfPageItemInfo:
    image_files: typing.List[str]
    file_name: str
class PdfPageInfo:
    main_file:str
    pages: typing.List[PdfPageItemInfo]
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
            for pdf_info in self.get_pdf_pages(file_path):
                ic(pdf_info.__dict__)
                print("OK")
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
    def get_pdf_pages(self, file_path:str)->typing.Iterable[PdfPageInfo]:
        ret = PdfPageInfo()
        rel_file_name = file_path[len(config.file_storage_path)+1:]
        tem_file_path = os.path.join(self.temp_dir,rel_file_name)
        tmp_dir_path = pathlib.Path(tem_file_path).parent.__str__()
        os.makedirs(tmp_dir_path,exist_ok=True)
        with open(file_path, "rb") as fr:
            with open(tem_file_path, "wb") as fw:
                fw.write(fr.read())

        # tem_file_path=os.path.join(pathlib.Path(tem_file_path).parent.__str__(),"CNBRVT_PKT_203_BC_BÁO CÁO THU PHÍ BỒI THƯỜNG_T9.2024_09.10.2024.pdf")
        # tem_file_path=r"/mnt/files/--tmp--/vietlotttest/2024/10/04/pdf/7da8a051-af2a-49da-83c4-6fe3a3dae3b4/CNBRVT_PKT_203_BC_BÁO CÁO THU PHÍ BỒI THƯỜNG_T9.2024_09.10.2024.pdf".replace(r"\\","/")
        # tmp_dir_path = pathlib.Path(tem_file_path).parent.__str__()
        tem_file_path=f"/mnt/files/--tmp--/qtscdemo/2024/10/10/pdf/201cf563-e971-447f-893f-5bd8e56b1e7a/data.pdf-version-1.pdf"
        tmp_dir_path = pathlib.Path(tem_file_path).parent.__str__()
        ret.main_file = tem_file_path
        ret.pages=[]
        with open(tem_file_path, 'rb') as pdf_file:
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
        yield ret





def main():
    runner = OCR()
    runner.do_ocr(runner.scaner_files.F.RegisterOn.desc())
if __name__ == "__main__":
    main()
# python cy_jobs/jobs/task_saas_ocr_recent.py app_name=all version=ocr-003