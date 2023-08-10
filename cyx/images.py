import os

import cy_kit
from cyx.base import Base
from cyx.media.core.graphics import GraphicsService


class ImageServices(Base):
    def __init__(
            self,
            graphics_service:GraphicsService=cy_kit.singleton(GraphicsService)
    ):
        self.init(__name__)
        self.pdf_convert_folder = os.path.join(self.processing_folder, "pdf_convert")
        if not os.path.isdir(self.pdf_convert_folder):
            os.makedirs(self.pdf_convert_folder, exist_ok=True)
        self.graphics_service:GraphicsService= graphics_service

    def create_thumbs(self, image_file_path, size: int = 350) -> str:
        ext_file =self.get_file_extenstion(image_file_path)

        try:
            filename_only = self.get_file_name_only(image_file_path)
            thumb_file_path = os.path.join(self.processing_folder, f"{filename_only}_{size}.webp")
            self.graphics.scale(
                source=image_file_path,
                dest = thumb_file_path,
                size=size
            )

            return thumb_file_path
        except Exception as e:
            self.logs.exception(e)

    def convert_to_pdf(self, image_file_path: str):
        file_name = self.get_file_name_only(image_file_path)
        ret = os.path.join(self.pdf_convert_folder, f"{file_name}.pdf")
        self.graphics.convert_to_pdf(
            source=image_file_path,
            dest =ret
        )
        return ret



