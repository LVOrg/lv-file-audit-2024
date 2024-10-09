import sys
import pathlib
import traceback
from typing import final

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import os
import time

import requests
from cy_jobs.jobs.lib_list_all_files import ListAllFilesService
from  retry import retry
from icecream import ic
from tika import parser as tika_parse
import cy_kit
from cyx.common import config
import PyPDF2
print(PyPDF2.__version__)
class NetOCRContent:
    list_all_files_service = cy_kit.singleton(ListAllFilesService)
    def __init__(self):
        self.url = "http://172.16.7.99:32270"
    def heal_check_remote_server(self)->bool:
        try:
            response = requests.head(self.url+"/swagger/index.html")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            return False

    import PyPDF2

    def remove_all_annotations(self,input_pdf):
        output_pdf_file_name =  f"{pathlib.Path(input_pdf).stem}.no-sinature{pathlib.Path(input_pdf).suffix}"
        output_pdf = os.path.join(pathlib.Path(input_pdf).parent.__str__(),output_pdf_file_name)

        with open(input_pdf, 'rb') as input_file, open(output_pdf, 'wb') as output_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()

            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                # Remove annotations (which might include signatures)

                if page.annotations:
                    page.annotations.clear()
                writer.add_page(page)

            writer.write(output_pdf )
            return output_pdf


    def get_content_form_tika(self,file_path):
        @retry(exceptions=(requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError), delay=15, tries=10)
        def runing():

            parsed_data = tika_parse.from_file(pdf_file,
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
    def heal_check_remote_server_until_ok(self):
        while not self.heal_check_remote_server():
            time.sleep(2)
    def upload_file_and_get_ocr_result(self,file_path):
        """Uploads a file to the specified endpoint and retrieves the OCR result.

        Args:
            file_path (str): The path to the file to be uploaded.

        Returns:
            dict: The OCR result as a JSON object.
        """

        url = self.url+ "/Document/get-ocr-result"

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
                    raise Exception(response.text())
            else:
                raise Exception("Error uploading file: " + response.text)

    def process_file(self):
        for file in self.list_all_files_service.get_files(
            file_type="pdf",
            filter_field_name="test-ocr",
            filter_value="test-006"
        ):
            try:
                ic(f"app_name={file.app_name} id={file.upload_id}")
                decrypt_file = file.decrypt_file()
                no_anotation_file = svc.remove_all_annotations(decrypt_file)
                if os.path.isfile(decrypt_file):
                    ret: str = self.upload_file_and_get_ocr_result(no_anotation_file)
                    with open(f"{decrypt_file}.txt","wb") as fs:
                        fs.write(ret.encode())
                    ic(decrypt_file)
                file.commit()
            except:
                print(traceback.format_exc())
            finally:
                file.commit()


if __name__ == "__main__":
    svc= cy_kit.singleton(NetOCRContent)
    # test_file=r'/root/python-2024/lv-file-fix-2024/py-files-sv/a_checking/resource-test/Ttr 425 tổ chức tri ân GĐ CBNV CNKH 2024.pdf'
    # txt = svc.get_content_form_tika(test_file)
    while True:
        svc.process_file()
        time.sleep(0.3)