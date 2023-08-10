import pathlib
import shutil
import typing

import cy_kit
from cyx.common.base import config
import subprocess
import uuid
import os

from cyx.common.share_storage import ShareStorageService
class LibreOfficeService:
    def __init__(self,share_storage_service = cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service
        self.config = config
        self.libre_office_path = self.config.libre_office_path
        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.temp_dir = self.share_storage_service.get_temp_dir(LibreOfficeService)
        self.user_profile_dir = os.path.join(self.temp_dir, "users-profiles")
        if not os.path.isdir(self.user_profile_dir):
            os.makedirs(self.user_profile_dir, exist_ok=True)
        self.output_dir = os.path.join(self.temp_dir, "out-put")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def get_image(self, file_path) -> str:
        """
        Generate image of file by using libre-office
        :param file_path:
        :return:
        """
        filename_only = pathlib.Path(file_path).stem
        ret_file = os.path.join(self.output_dir, f"{filename_only}.png")
        if os.path.isfile(ret_file):
            return ret_file

        uno = f"Negotiate=0,ForceSynchronous=1;"
        # from subprocess import CREATE_NEW_CONSOLE

        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(self.user_profile_dir, user_profile_id)

        pid = subprocess.Popen(
            [
                self.libre_office_path,
                '--headless',
                '--convert-to', 'png',
                f"--accept={uno}",
                f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
                '--outdir',
                self.output_dir, file_path
            ],
            shell=False,
            start_new_session=True
            # creationflags=16
        )
        ret = pid.wait()  # Đợi

        return ret_file

    def convert_to_pdf(self, file_path):
        """
                Generate image of file by using libreoffice
                :param file_path:
                :return:
                """
        filename_only = pathlib.Path(file_path).stem
        file_extension = os.path.splitext(file_path)[1][1:]
        ret_file = os.path.join(self.output_dir, f"{filename_only}.pdf")
        if os.path.isfile(ret_file):
            return ret_file
        if os.path.isfile(ret_file):
            return ret_file

        uno = f"Negotiate=0,ForceSynchronous=1;"
        # from subprocess import CREATE_NEW_CONSOLE

        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(self.user_profile_dir, user_profile_id)
        # convert longfile.pdf[0-1,3] output.pdf //libre office convert
        # pdf:draw_pdf_Export:{"PageRange":{"type":"string","value":"2-"}}
        pid = subprocess.Popen(
            [
                self.libre_office_path,
                '--headless',
                '--convert-to', 'pdf',
                f"--accept={uno}",
                f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
                '--outdir',
                self.output_dir, f"{file_path}"
            ],
            shell=False,
            start_new_session=True
            # creationflags=16
        )

        ret = pid.wait()  # Đợi
        if ret == 0:
            return ret_file
        else:
            return None

    def extract_pages_content(self, file_path) -> typing.List[str]:
        pdf_file = self.convert_to_pdf(file_path)
        ret =[]
        if pdf_file:
            import fitz
            from PIL import Image
            # Opening the PDF file and creating a handle for it
            file_handle = fitz.open(pdf_file)
            for x in file_handle:
                ret+=[x.get_text()]
            os.remove(pdf_file)
        return ret

            # The page no. denoted by the index would be loaded
            # The index within the square brackets is the page number
