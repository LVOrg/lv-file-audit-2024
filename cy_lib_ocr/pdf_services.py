"""
PDF service serve for ocr
This package extract all image from PDF file
"""
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os
import typing

import fitz
import PIL
import hashlib
from icecream import ic
import io
from PyPDF2 import PdfReader
import PyPDF2.errors
import PIL.Image
import  retry
import requests
import cy_kit
from cy_lib_ocr.detect_orientation_mage_service import OrientDetector
from  tika import parser as tika_parse
from cyx.common import config
class PDF_Service:
    orient_detector = cy_kit.single(OrientDetector)
    def get_dir_by_hash_name(self, pdf_file_path)->str:
        """
        THis method create new name by hash256 of pdf_file_path
        @param pdf_file_path:
        @return:
        """
        return hashlib.sha256(pdf_file_path.encode()).hexdigest()
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



    def get_pixmaps_in_pdf(self,pdf_filename):
        doc = fitz.open(pdf_filename)
        xrefs = set()
        for page_index in range(doc.pageCount):
            for image in doc.getPageImageList(page_index):
                xrefs.add(image[0])  # Add XREFs to set so duplicates are ignored
        pixmaps = [fitz.Pixmap(doc, xref) for xref in xrefs]
        doc.close()
        return pixmaps

    def image_extract(self, pdf_file_path: str, output_dir: str) -> typing.Iterable[str]:
        child_dir: str = self.get_dir_by_hash_name(pdf_file_path)
        child_output_dir = os.path.join(output_dir, child_dir)
        os.makedirs(child_output_dir, exist_ok=True)
        raw_images= self.raw_extract_images(pdf_file_path)
        i = 0
        for img in raw_images:
            image_file_name = f"{i}.png"
            image_file_path = os.path.join(child_output_dir, image_file_name)
            if hasattr(img,"writePNG") and callable(img.writePNG):
                img.writePNG(image_file_path)
            else:
                img.save(image_file_path, 'png')
            i+=1
            # pixmap.writePNG(image_file_path)
            # pre_image_file_path =self.orient_detector.pre_process_image(image_file_path)
            yield image_file_path # Might want to come up
    def image_extract_delete(self,pdf_file_path:str,output_dir:str)->typing.Iterable[str]:
        """
        Extracts all images from a PDF file to the specified output directory and returns a list of image paths.

        Args:
            pdf_file_path (str): The path to the PDF file.
            output_dir (str): The path to the output directory where images will be saved.

        Returns:
            list[str]: A list of paths to the extracted images.
        """
        child_dir:str = self.get_dir_by_hash_name(pdf_file_path)
        child_output_dir = os.path.join(output_dir,child_dir)
        os.makedirs(child_output_dir,exist_ok=True)

        doc = fitz.open(pdf_file_path)

        for i in range(len(doc)):
            for img in doc.get_page_images(i):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:  # this is GRAY or RGB
                    image_file_name = "p%s-%s.png" % (i, xref)
                    image_file_path = os.path.join(child_output_dir,image_file_name)

                    pix._writeIMG(image_file_path,format=1)
                    # pix._writeIMG(format= None,jpg_quality =None,filename=image_file_path)
                    ic(image_file_path)
                    yield image_file_path
                else:  # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    image_file_name = "p%s-%s.png" % (i, xref)
                    image_file_path = os.path.join(child_output_dir, image_file_name)
                    pix1._writeIMG(image_file_path,format=1)
                    pix1 = None
                    ic(image_file_path)
                    yield image_file_path
                pix = None
    def extract_text_by_using_tika_server(self, file_path:str):
        @retry(exceptions=(requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError),delay=15,tries=10)
        def runing():

            parsed_data = tika_parse.from_file(file_path,
                                               serverEndpoint=config.tika_server,
                                               xmlContent = False,
                                               requestOptions = {'timeout': 5000})

            content = parsed_data.get("content","") or ""
            content = content.lstrip('\n').rstrip('\n').replace('\n',' ').replace('\r',' ').replace('\t',' ')
            while "  " in content:
                content = content.replace("  "," ")
            content = content.rstrip(' ').lstrip(' ')
            return content
        return runing()

    def read_text_from_file(self,pdf_file)->str:
        contents = []
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            contents.append(page.extract_text())
        del reader
        return " ".join(contents)



def main():
    svc = PDF_Service()
    pdf_file = r'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/511-cp.signe.pdf'
    pdf_file = r'/app/a_checking/resource-test/Bản tin tháng 9.pdf'
    output_dir = f'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/results'
    output_dir = r'/app/a_checking/resource-test/results'
    file_iter: typing.Iterable[str] = svc.image_extract(pdf_file_path=pdf_file,output_dir=output_dir)
    for x in file_iter:
        print(x)
if __name__ == "__main__":
    # run on venv-ocr-311 (python 3.11)
    main()
## docker run   -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app -v /mnt/files:/mnt/files docker.lacviet.vn/xdoc/composite-ocr:2.1.19 python /app/cy_lib_ocr/pdf_services.py