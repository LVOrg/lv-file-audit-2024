import mimetypes
import os.path
import pathlib
from PIL import Image
import img2pdf
import cy_web
import cy_kit
from cyx.media.video import VideoServices
from cyx.media.libre_office import LibreOfficeService
from cyx.media.pdf import PDFService
from cyx.media.exe import ExeService
from cyx.media.core.graphics import GraphicsService
from cyx.base import config

from cyx.common.share_storage import ShareStorageService
class ImageExtractorService:
    def __init__(
            self,
            video_service: VideoServices = cy_kit.singleton(VideoServices),
            libre_office_service: LibreOfficeService = cy_kit.singleton(LibreOfficeService),
            pdf_service: PDFService = cy_kit.singleton(PDFService),
            exe_service: ExeService = cy_kit.singleton(ExeService),
            graphics_service: GraphicsService = cy_kit.singleton(GraphicsService),
            share_storage_service:ShareStorageService = cy_kit.singleton(ShareStorageService)
    ):
        self.share_storage_service = share_storage_service
        self.video_service: VideoServices = video_service
        self.libre_office_service = libre_office_service
        self.pdf_service = pdf_service
        self.exe_service = exe_service
        self.config = config
        self.ext_office_file = self.config.ext_office_file
        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.processing_folder = self.share_storage_service.get_temp_dir(ImageExtractorService)
        self.processing_tmp_pdf_folder = os.path.join(
            self.processing_folder,"pdf"
        )
        if not os.path.isdir(self.processing_tmp_pdf_folder):
            os.makedirs(self.processing_tmp_pdf_folder,exist_ok= True)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder,exist_ok=True)
        self.graphics_service: GraphicsService = graphics_service
        self.logs = cy_kit.create_logs(self.share_storage_service.get_logs_dir(ImageExtractorService),ImageExtractorService.__name__)

    def get_image(self, file_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(file_path)
        file_ext = os.path.splitext(file_path)[1][1:]
        if mime_type.startswith("video/"):
            return self.video_service.get_image(file_path)
        if mime_type.startswith("image/"):
            return file_path
        if file_ext == "pdf":
            return self.pdf_service.get_image(file_path)
        if file_ext == "exe":
            return self.exe_service.get_image(file_path)
        if file_ext in self.ext_office_file:
            return self.libre_office_service.get_image(file_path)
        return None

    def create_thumb(self, image_file_path, size:int):
        try:
            filename_only = pathlib.Path(image_file_path).stem
            thumb_file_path = os.path.join(self.processing_folder, f"thumbnail_{filename_only}_{size}.webp")
            if os.path.isfile(thumb_file_path):
                return thumb_file_path
            self.graphics_service.scale(
                source=image_file_path,
                dest=thumb_file_path,
                size=size
            )

            return thumb_file_path
        except Exception as e:
            self.logs.exception(e)
            raise e

    def convert_to_pdf(self, file_path,file_ext=None):
        if file_ext is None:
            pdf_file = os.path.join(
                self.processing_tmp_pdf_folder, f"{pathlib.Path(file_path).stem}{os.path.splitext(file_path)[1]}"
            )
        else:
            pdf_file = os.path.join(
                self.processing_tmp_pdf_folder, f"{pathlib.Path(file_path).stem}.{file_ext}"
            )
        if os.path.isfile(pdf_file):
            return pdf_file
        image = Image.open(file_path)
        pdf_bytes = img2pdf.convert(image.filename)
        file = open(pdf_file, "wb")
        file.write(pdf_bytes)
        image.close()
        file.close()
        del image
        del file
        cy_kit.clean_up()
        return pdf_file


    
