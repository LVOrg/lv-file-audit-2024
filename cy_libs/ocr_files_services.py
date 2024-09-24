"""
This will call nttlong/ocr-my-pdf-api:12
"""
import os.path
import pathlib
import sys
from icecream import ic
import PyPDF2
import hashlib
import io
from PIL import Image

from reportlab.pdfgen import canvas

from cyx.common import config
from cyx.repository import Repository

working_dir = pathlib.Path(__file__).parent.parent.__str__()
ic(working_dir)

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
sys.path.append("/app")
import cy_kit
import time
import subprocess
from cyx.rabbit_utils import Consumer
import PIL
import PyPDF2.errors
import typing
def ___extract_pdf_text__(input_pdf_path):
    """Extracts text from a PDF file and returns it as a string.

    Args:
        input_pdf_path (str): Path to the input PDF file.

    Returns:
        str: Extracted text from the PDF file.
    """

    with open(input_pdf_path, 'rb') as input_pdf:
        pdf_reader = PyPDF2.PdfReader(input_pdf)

        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()

    return extracted_text

def __do_make_pdf_a_file___(x_file:str):
    page_out_put=f"{x_file}-a.pdf"
    if os.path.isfile(page_out_put):
        return page_out_put
    ic(f"do orc file {x_file} and out put {page_out_put}")
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
    return page_out_put if os.path.isfile(page_out_put) else None
from cy_libs.text_files_servcices import ExtractTextFileService
class PdfPageInfo:
    """
    This class store info of PDF fie after splitting
    """
    page_file_path: str
    """
    Child page
    """
    image_file_list: typing.List[str]=[]
    """
    List of images in Child page
    """
    pdf_file_list: typing.List[str] = []
    pdf_a_file_list: typing.List[str] = []
    text_content: str
    text_content_from_tika: str
    text_content_from_ocr: str
    """
    Text content of Child Page
    """
class PdfAnalyzerInfo:
    """
    Analyzer info of pdf file
    """
    __pdf_file_path__: str
    """
    Physical path of original pdf file
    """
    pages: typing.List[PdfPageInfo]=[]
    """
    Children pages info
    """
    __dir_name__: typing.Union[str]
    __temp_dir_path__: typing.Union[str]
    def __init__(self,temp_dir_path:str):
        self.__temp_dir_path__ = temp_dir_path
    @property
    def pdf_file_path(self)->str:
        return self.__pdf_file_path__
    @pdf_file_path.setter
    def pdf_file_path(self,value:str):
        self.__pdf_file_path__ = value
        self.__dir_name__ = hashlib.sha256(self.__pdf_file_path__.encode()).hexdigest()

    @property
    def out_put_dir_name(self)->str:
        if self.__dir_name__ is None:
            raise Exception(f"You must call set_pdf_file_path or assign pdf_file_path before call this method")
        return self.__dir_name__
    @property
    def output_dir_path(self)->str:
        ret = os.path.join(self.__temp_dir_path__,self.out_put_dir_name)
        os.makedirs(ret, exist_ok=True)
        return ret
    def get_output_pdf_path(self, child_page_index:int):
        return os.path.join(self.output_dir_path,f"{child_page_index}.pdf")

    def get_text_from_ocr(self)->str:
        return  " ".join([page.text_content_from_ocr or "" for page in self.pages])

    def get_text_from_pdf(self):
        return  " ".join([page.text_content_from_tika or "" for page in self.pages])

    def get_full_text(self, wel_form_text:bool=True):
        ret = self.get_text_from_ocr()+ ' '+self.get_text_from_pdf()
        if wel_form_text:
            ret = ret.replace('\n',' ').replace('\r',' ').replace('\t',' ')
            ret = ret.rstrip(" ").lstrip(' ')
            while '  ' in ret:
                ret = ret.replace('  ',' ')
        return ret


class OCRFilesService(ExtractTextFileService):
    def __init__(self):
        super().__init__()
        self.__ocr_dir__ = os.path.join(self.__temp_dir__,"__orc_dir__")
        os.makedirs(self.__ocr_dir__,exist_ok=True)
        self.__pre_post__ = None
    @property
    def ocr_dir(self):
        """
        Physical path to temp directory ocr processing
        @return:
        """
        return self.__ocr_dir__


    def extract_pages(self, file_path)->PdfAnalyzerInfo:
        ret = PdfAnalyzerInfo(
            temp_dir_path= self.ocr_dir
        )
        ret.pdf_file_path = file_path

        with open(file_path, 'rb') as input_pdf:
            pdf_reader = PyPDF2.PdfReader(input_pdf)

            # Iterate over the specified page numbers and add them to the new PDF
            child_page_index = 0
            for pdf_page in  pdf_reader.pages:
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(pdf_page)
                output_pdf_path: str = ret.get_output_pdf_path(child_page_index)
                # Save the new PDF
                with open(output_pdf_path, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                child_page_index += 1
                child_page= PdfPageInfo()
                child_page.page_file_path = output_pdf_path


                ret.pages+=[child_page]
        return ret


    def extract_images(self, pdf_analyzer_info:PdfAnalyzerInfo):
        image_id = 0

        for child_page in pdf_analyzer_info.pages:
            child_page.image_file_list = []
            output_dir_of_images = pathlib.Path(child_page.page_file_path).parent.__str__()
            with open(child_page.page_file_path, 'rb') as input_pdf:
                pdf_reader = PyPDF2.PdfReader(input_pdf)

                for page_number, page in enumerate(pdf_reader.pages):
                    if not page.get('/Resources') or not isinstance(page.get('/Resources'),dict):
                        continue
                    if not page.get('/Resources').get('/XObject'):
                        continue
                    for obj in page['/Resources']['/XObject']:
                        if page['/Resources']['/XObject'][obj]['/Subtype'] == '/Image':
                            try:
                                image_data = page['/Resources']['/XObject'][obj].get_data()
                                image_data_io = io.BytesIO(image_data)
                                image = Image.open(image_data_io)

                                # Save the image to the output folder with a suitable filename
                                image_filename = f"{page_number + 1}_{image_id}.jpg"  # Adjust filename format as needed
                                image_file_path = os.path.join(output_dir_of_images,image_filename)
                                image.save(image_file_path)
                                child_page.image_file_list+=[image_file_path]
                                image_id+=1
                            except NotImplementedError as ex:
                                continue
                            except PIL.UnidentifiedImageError as ex:
                                continue
        return  pdf_analyzer_info


    def extract_text_of_pdf_page_by_tika(self, pdf_analyzer_info:PdfAnalyzerInfo):
        for page_info in pdf_analyzer_info.pages:
            page_info.text_content_from_tika =  self.extract_text_by_using_tika_server(page_info.page_file_path)
        return pdf_analyzer_info


    def create_pdf_a(self, pdf_analyzer_info:PdfAnalyzerInfo)->PdfAnalyzerInfo:
        for page_info in pdf_analyzer_info.pages:
            page_info.pdf_a_file_list = []
            for pdf_file in page_info.pdf_file_list:
                pdf_a_file = __do_make_pdf_a_file___(pdf_file)
                if os.path.isfile(pdf_a_file):
                    page_info.pdf_a_file_list += [pdf_a_file]

        return  pdf_analyzer_info

    def extract_text_of_pdf_page_by_pdf_a(self, pdf_analyzer_info:PdfAnalyzerInfo)->PdfAnalyzerInfo:
        for page_info in pdf_analyzer_info.pages:
            txt_contents =[]
            for pdf_a_file in page_info.pdf_a_file_list:
                txt_contents.append(___extract_pdf_text__ (pdf_a_file))
            page_info.text_content_from_ocr = " ".join(txt_contents)
        return pdf_analyzer_info


    def convert_images_to_pdf(self, pdf_analyzer_info:PdfAnalyzerInfo)->PdfAnalyzerInfo:
        for page_info in pdf_analyzer_info.pages:
            page_info.pdf_file_list = []
            for image_path in page_info.image_file_list:
                output_pdf_path= f"{image_path}.pdf"
                with Image.open(image_path) as image:
                    width, height = image.size

                    # Create a PDF canvas with the image size as page size
                    pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=(width, height))

                    # Draw the image on the canvas
                    pdf_canvas.drawImage(image_path, 0, 0, width=width, height=height)

                    # Save the PDF
                    pdf_canvas.save()
                    page_info.pdf_file_list+=[output_pdf_path]
        return pdf_analyzer_info


        pass
    def producer_ocr_content(self, app_name:str, msg:str):
        if not self.__producer__:
            self.__producer__= Consumer(msg)
        agg = Repository.files.app(app_name).context.aggregate().match(
            Repository.files.fields.Status==1
        ).match(
            Repository.files.fields.FileExt=="pdf"
        ).match(
            (Repository.files.fields.HasORCContent==None)|(Repository.files.fields.HasORCContent==False)
        ).match(
            Repository.files.fields.MsgOCRReRaise!=msg

        ).sort(
            Repository.files.fields.RegisterOn.desc()
        ).limit(1)
        for item in agg:
            self.__producer__.raise_message(
                app_name=app_name,
                data=item.to_json_convertable(),
                msg_type=msg
            )
            ic(f"raise msg={msg} in app={app_name}")
            ic(item.to_json_convertable())
            self.update_upload_ocr_content(app_name=app_name, upload_id=item.id, msg=msg)

    def update_upload_ocr_content(self, app_name, upload_id,msg):
        Repository.files.app(app_name).context.update(
            Repository.files.fields.id==upload_id,
            Repository.files.fields.MsgOCRReRaise<<msg
        )
    def set_pre_post(self,fn):
        self.__pre_post__ = fn
    def consumer_ocr_content(self, msg):
        if not self.__producer__:
            self.__producer__ = Consumer(msg)
        rb_msg = self.__producer__.get_msg(delete_after_get=False)
        if not rb_msg:
            time.sleep(1)
            return
        data = rb_msg.data
        main_file_id:str = data.get(Repository.files.fields.MainFileId.__name__) or ""
        if main_file_id=="" or "://" not in main_file_id:
            self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_ocr_content(
                app_name = rb_msg.app_name,
                upload_id = data.get("_id"),
                msg=msg
            )
            return
        rel_encrypted_file_path = main_file_id.split("://")[1]
        encrypted_file_path = os.path.join(config.file_storage_path.replace('/',os.sep),rel_encrypted_file_path)
        if not os.path.isfile(encrypted_file_path):
            self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_ocr_content(
                app_name=rb_msg.app_name,
                upload_id=data.get("_id"),
                msg=msg
            )
            return
        decrypted_file_path = self.decrypt_file(encrypted_file_path)
        if self.__pre_post__ and callable(self.__pre_post__):
            content_file_path = self.__pre_post__(decrypted_file_path)
            data["content-file"] = content_file_path
            self.__producer__.raise_message(
                app_name=rb_msg.app_name,
                data=data,
                msg_type=f"{msg}_es_update"
            )
            self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_office_content(app_name=rb_msg.app_name, upload_id=data.get("_id"), msg=msg)
            return
        try:
            pdf_analyzer_info: PdfAnalyzerInfo = self.extract_pages(
                file_path=decrypted_file_path
            )
            pdf_analyzer_info = self.extract_images(pdf_analyzer_info=pdf_analyzer_info)
            pdf_analyzer_info = self.convert_images_to_pdf(pdf_analyzer_info=pdf_analyzer_info)
            pdf_analyzer_info = self.extract_text_of_pdf_page_by_tika(pdf_analyzer_info)
            pdf_analyzer_info = self.create_pdf_a(pdf_analyzer_info)
            pdf_analyzer_info = self.extract_text_of_pdf_page_by_pdf_a(pdf_analyzer_info)
            text_from_ocr: str = pdf_analyzer_info.get_text_from_ocr()
            text_from_pdf: str = pdf_analyzer_info.get_text_from_pdf()
            full_text: str = pdf_analyzer_info.get_full_text()
            dir_of_server_file = pathlib.Path(decrypted_file_path).parent.__str__()
            content_of_server_file_es = os.path.join(dir_of_server_file, pathlib.Path(decrypted_file_path).stem + ".content.txt")
            with open(content_of_server_file_es, "wb") as fs:
                fs.write(full_text.encode())
            data["content-file"] = content_of_server_file_es
            self.__producer__.raise_message(
                app_name=rb_msg.app_name,
                data=data,
                msg_type=f"{msg}_es_update"
            )
            self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_office_content(app_name=rb_msg.app_name, upload_id=data.get("_id"), msg=msg)
        except :
            pdf_a_file_path = __do_make_pdf_a_file___(decrypted_file_path)
            if not pdf_a_file_path or not os.path.isfile(pdf_a_file_path):
                ic(f"Uss Tika server extract content {decrypted_file_path}")
                text_contents = self.extract_text_by_using_tika_server(decrypted_file_path)
            else:
                text_contents = ___extract_pdf_text__(pdf_a_file_path)
            ic(text_contents[:20])
            dir_of_server_file = pathlib.Path(decrypted_file_path).parent.__str__()
            content_of_server_file_es = os.path.join(dir_of_server_file,
                                                     pathlib.Path(decrypted_file_path).stem + ".content.txt")
            with open(content_of_server_file_es, "wb") as fs:
                fs.write(text_contents.encode())
            data["content-file"] = content_of_server_file_es
            self.__producer__.raise_message(
                app_name=rb_msg.app_name,
                data=data,
                msg_type=f"{msg}_es_update"
            )
            self.__producer__.channel.basic_ack(rb_msg.method.delivery_tag)
            self.update_upload_office_content(app_name=rb_msg.app_name, upload_id=data.get("_id"), msg=msg)


def main():
    test_file=r'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/511-cp.signe.pdf'
    # test_file = r'/app/a_checking/resource-test/511-cp.signe.pdf'
    svc = cy_kit.singleton(OCRFilesService)
    ic(svc.decrypt_dir)
    pdf_analyzer_info:PdfAnalyzerInfo = svc.extract_pages(
        file_path=test_file
    )
    pdf_analyzer_info = svc.extract_images(pdf_analyzer_info=pdf_analyzer_info)
    pdf_analyzer_info = svc.convert_images_to_pdf(pdf_analyzer_info=pdf_analyzer_info)
    pdf_analyzer_info = svc.extract_text_of_pdf_page_by_tika(pdf_analyzer_info)
    pdf_analyzer_info = svc.create_pdf_a(pdf_analyzer_info)
    pdf_analyzer_info = svc.extract_text_of_pdf_page_by_pdf_a(pdf_analyzer_info)
    text_from_ocr:str = pdf_analyzer_info.get_text_from_ocr()
    text_from_pdf:str  = pdf_analyzer_info.get_text_from_pdf()
    full_text:str = pdf_analyzer_info.get_full_text()

    print(text_from_pdf)
    ic(pdf_analyzer_info.__dict__)

if __name__ == "__main__":
    main()
#test
#docker run -it --entrypoint=/bin/bash -v /mnt/files:/mnt/files -v /root/python-2024/lv-file-fix-2024/py-files-sv:/app   docker.lacviet.vn/xdoc/lib-ocr-all:31
#python3 cy_jobs/jobs/task_msg_consumer_ocr.py app_name=developer msg_ocr=developer-001
#python3 cy_jobs/jobs/task_msg_es_update_ocr.py app_name=developer msg_ocr=developer-001
#python3 cy_jobs/jobs/task_msg_producer_ocr.py app_name=developer msg_ocr=developer-001