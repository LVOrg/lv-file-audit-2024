import datetime
import os
import pathlib
import shutil
import time
import typing
import uuid

import pdfplumber

import glob
import PyPDF2.errors
import PyPDF2

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfMerger
import PyPDF2.errors
from pdfminer.pdfpage import PDFPage
import cy_kit

from cyx.common.share_storage import ShareStorageService
from cyx.loggers import LoggerService
import fitz
class PDFService:
    def __init__(self,
                 share_storage_service: ShareStorageService = cy_kit.singleton(ShareStorageService),
                 logger= cy_kit.singleton(LoggerService)):
        self.share_storage_service = share_storage_service
        self.processing_folder = self.share_storage_service.get_temp_dir(PDFService)
        self.logger = logger
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder, exist_ok=True)
        os.environ["PATH"] += ":/home/vmadmin/python/cy-py/docker-cy-hack/gs/bin:/home/vmadmin/python/cy-py/docker-cy-hack/gs/bin/gs"
        self.__easyocr_reader_dict__ = {}

    def get_image(self, file_path: str):
        import fitz
        pdf_file = file_path
        filename_only = pathlib.Path(pdf_file).stem
        unique_dir = pathlib.Path(file_path).parent.__str__()

        image_file_path = os.path.join(unique_dir, f"{filename_only}.png")
        if os.path.isfile(image_file_path):
            return image_file_path
        if os.path.isfile(image_file_path):
            return image_file_path
        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
        self.logger.info(f"split file {pdf_file}")
        all_files = glob.glob(pdf_file)
        self.logger.info(f"split file {pdf_file} is ok")


        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save(image_file_path)  # store image as a PNG
                break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
            break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
        return image_file_path

    def convert_to_image(self, file_path: str, out_put_dir=None, page_number=None) -> str:
        import cv2
        pdf_file = file_path
        filename_only = pathlib.Path(pdf_file).stem
        __out_put_dir__ = out_put_dir or self.processing_folder
        image_file_path = os.path.join(__out_put_dir__, f"{filename_only}.png")

        all_files = glob.glob(pdf_file)
        i = 0
        images_file = []
        tmp_file_name = str(uuid.uuid4())
        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages

                pix = page.get_pixmap()  # render page to an image
                temp_img = os.path.join(__out_put_dir__, f"{tmp_file_name}_{i}.png")
                pix.save(temp_img)  # store image as a PNG

                images_file += [temp_img]
                if page_number is not None and page_number == i:
                    break
                i += 1
        images = []
        for x in images_file:
            images = [cv2.imread(x)]

        im_v = cv2.vconcat(images)
        cv2.imwrite(image_file_path, im_v)
        for x in images_file:
            os.remove(x)

        return image_file_path

    def convert_to_images(self, file_path: str, out_put_dir=None) -> typing.List[str]:
        import fitz
        pdf_file = file_path
        filename_only = pathlib.Path(pdf_file).stem
        __out_put_dir__ = out_put_dir or self.processing_folder

        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        all_files = glob.glob(pdf_file)
        i = 0
        image_file_paths = []
        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                image_file_path = os.path.join(__out_put_dir__, f"{filename_only}_page_{i}_.png")
                pix = page.get_pixmap()  # render page to an image
                pix.save(image_file_path)  # store image as a PNG
                i += 1
                image_file_paths += [image_file_path]
        return image_file_paths

    def get_pdf_searchable_pages(self, fname):
        searchable_pages = []
        non_searchable_pages = []
        # ascii_trip = bytes([0x0c]).decode('ascii')
        with open(fname, 'rb') as infile:

            page_num = 0
            for page in PDFPage.get_pages(infile):

                page_num += 1
                if 'Font' in page.resources.keys():
                    if len(page.contents)>0 and hasattr(page.contents[0],"data") and  isinstance(page.contents[0].data,bytes) and  page.contents[0].data.decode('utf8').__len__()>256:
                        searchable_pages.append(page_num - 1)
                    else:
                        non_searchable_pages.append(page_num - 1)
                else:
                    non_searchable_pages.append(page_num - 1)

        return searchable_pages, non_searchable_pages

    def get_text(self, pdf_file_path) -> bool:
        """
               Check is pdf file ready ORC?
               :param file_path:
               :return:
               """
        if not os.path.isfile(pdf_file_path):
            return ""
        ret = ""
        with pdfplumber.open(pdf_file_path) as pdf:
            """
            Check have pdf file been ORC?
            """
            if pdf.pages.__len__() == 0:
                """
                Nothing to do
                """
                return ret
            for page in pdf.pages:
                text = page.extract_text()

                ret += text
            return ret

    def has_text(self, pdf_file_path) -> bool:
        """
               Check is pdf file ready ORC?
               :param file_path:
               :return:
               """
        if not os.path.isfile(pdf_file_path):
            return True

        with pdfplumber.open(pdf_file_path) as pdf:
            """
            Check have pdf file been ORC?
            """
            if pdf.pages.__len__() == 0:
                """
                Nothing to do
                """
                return True
            for page in pdf.pages:
                text = page.extract_text()
                text = text.strip('\n').strip('\t').strip(' ')
                if text.__len__() > 0:
                    return True
            return False
    def get_easyocr_reader(self, langs:typing.List[str]):
        import easyocr
        key = "___".join(langs)
        if self.__easyocr_reader_dict__.get(key) is None:
            self.__easyocr_reader_dict__[key] = easyocr.Reader(langs)
        return self.__easyocr_reader_dict__.get(key)
    def ocr_text(self, pdf_file):

        inputpdf = None
        try:
            inputpdf = PdfFileReader(stream=open(pdf_file, "rb"), strict=False)
        except:
            inputpdf = PdfFileReader(stream=open(pdf_file, "rb"))
        if inputpdf is None:
            return self.get_text(pdf_file)

        split_dir = os.path.join(self.processing_folder, "spliter")
        os.makedirs(split_dir,exist_ok=True)
        file_name_only = pathlib.Path(pdf_file).stem
        text = ""
        for i in range(inputpdf.numPages):
            output = PdfFileWriter()
            inputpdf.getPage(i)
            output.addPage(inputpdf.getPage(i))
            output_page = os.path.join(split_dir, f"{file_name_only}.{i}.pdf")
            print(f"Process {output_page} ...")

            with open(output_page, "wb") as outputStream:
                output.write(outputStream)
            img = self.get_image(output_page)
            langs = ['vi', 'en']
            text += " ".join(self.get_easyocr_reader(langs=langs).readtext(img,detail=0))
            text += " "+self.get_text(output_page)
            print(f"Process {output_page} was completed")
        try:
            shutil.rmtree(split_dir)
        except:
            pass
        return text



    def ocr(self, pdf_file, scale=1, deskew=True)->typing.Optional[str]:
        """
                        Thuc hien ocr pdf file trong tien tring rieng biet skip if all pages are searchable
                        :param file_path:
                        :param out_put_file_path:
                        :return:
                        """
        split_dir = os.path.join(self.processing_folder, "spliter")
        file_name_only = pathlib.Path(pdf_file).stem
        out_put_file_path = os.path.join(self.processing_folder, f"{file_name_only}.pdf")
        try:
            if not os.path.isdir(split_dir):
                os.makedirs(split_dir, exist_ok=True)
            try:
                inputpdf = PdfFileReader(stream=open(pdf_file, "rb"),strict=False)
            except PyPDF2.errors.PdfStreamError:
                return pdf_file
            pdfs = []
            pdfs_files = []
            self.logger.info(f"detect searchable_pages{pdf_file}...")
            searchable, non_searchable = self.get_pdf_searchable_pages(pdf_file)
            self.logger.info(f"detect searchable_pages{pdf_file} was complete")
            if non_searchable.__len__() == 0:
                self.logger.info(f"all page in {pdf_file} was searchable")
                return pdf_file

            for i in range(inputpdf.numPages):
                output = PdfFileWriter()
                inputpdf.getPage(i).scale(sx=scale, sy=scale)
                output.addPage(inputpdf.getPage(i))
                output_page = os.path.join(split_dir, f"{file_name_only}.{i}.pdf")
                output_ocr = os.path.join(split_dir, f"{file_name_only}.ocr.{i}.pdf")
                start = datetime.datetime.utcnow()
                with open(output_page, "wb") as outputStream:
                    output.write(outputStream)
                self.logger.info(f"orc start  {output_page} {start}")
                import ocrmypdf
                if i in non_searchable:
                    ocrmypdf.ocr(
                        input_file=output_page,
                        output_file=output_ocr,
                        progress_bar=False,
                        language="vie+eng",
                        use_threads=False,
                        skip_text=False,
                        force_ocr=True,
                        deskew=deskew,

                        # jobs=50,
                        # optimize=3,
                        keep_temporary_files=False
                    )
                    if os.path.isfile(output_ocr):
                        pdfs += [output_ocr]
                    else:
                        pdfs += [output_page]
                    pdfs_files += [output_page]
                    time.sleep(0.5)

                else:
                    pdfs += [output_page]
                    pdfs_files += [output_page]
                n = (datetime.datetime.utcnow() - start).total_seconds() * 1000

                self.logger.info(f"orc time of  {output_page} {(n)} millisecond")
                del output
                cy_kit.clean_up()

            merger = PdfMerger()
            self.logger.info(f"OCR Merger file")
            for pdf in pdfs:
                self.logger.info(f"Merger run  {pdf}")
                merger.append(pdf)
                cy_kit.clean_up()
            self.logger.info(f"Merger write  {out_put_file_path}")
            merger.write(out_put_file_path)
            merger.close()
            del merger
            for pdf in pdfs:
                if os.path.isfile(pdf):
                    os.remove(pdf)
            for pdf in pdfs_files:
                if os.path.isfile(pdf):
                    os.remove(pdf)
            cy_kit.clean_up()
            return out_put_file_path
        except PyPDF2.errors.PdfReadError as e:
            self.logger.error(e)
            ocrmypdf.ocr(
                input_file=pdf_file,
                output_file=out_put_file_path,
                progress_bar=False,
                language="vie+eng",
                use_threads=False,
                skip_text=False,
                force_ocr=True,
                deskew=True,

                # jobs=50,
                # optimize=3,
                keep_temporary_files=False
            )
            cy_kit.clean_up()
            return out_put_file_path
        except Exception as e:
            self.logger.error(e)
    def ocr_depriciate(self, pdf_file):
        """
                        Thuc hien ocr pdf file trong tien tring rieng biet
                        :param file_path:
                        :param out_put_file_path:
                        :return:
                        """
        file_name_only = pathlib.Path(pdf_file).stem
        out_put_file_path = os.path.join(self.processing_folder, f"{file_name_only}.pdf")
        fx = ocrmypdf.ocr(
            input_file=pdf_file,
            output_file=out_put_file_path,
            progress_bar=False,
            language="vie+eng",
            use_threads=False,
            skip_text=False,
            force_ocr=True,
            jobs=100,
            keep_temporary_files=False
        )
        return out_put_file_path








