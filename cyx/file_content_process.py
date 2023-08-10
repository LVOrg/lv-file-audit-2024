import os
import pathlib

import cy_docs

from cyx.common.msg import MessageService, MessageInfo
from cyx.media.image_extractor import ImageExtractorService
from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
from cy_xdoc.services.files import FileServices
from cyx.media.pdf import PDFService
from cyx.media.contents import ContentsServices
import cy_web
import mimetypes
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
from cyx.common.base import config
class FileContentProcessService:
    def __init__(
            self,
            image_extractor_service: ImageExtractorService = cy_kit.singleton(ImageExtractorService),
            file_storage_services: MongoDbFileService = cy_kit.singleton(MongoDbFileService),
            file_services: FileServices = cy_kit.singleton(FileServices),
            pdf_services: PDFService = cy_kit.singleton(PDFService),
            contents_services: ContentsServices = cy_kit.singleton(ContentsServices),
            search_engine: SearchEngine = cy_kit.singleton(SearchEngine)

    ):
        self.image_extractor_service = image_extractor_service
        self.file_storage_services: MongoDbFileService = file_storage_services
        self.file_services: FileServices = file_services
        self.pdf_services: PDFService = pdf_services
        self.contents_services: ContentsServices = contents_services
        self.search_engine: SearchEngine = search_engine
        self.config = config
        self.ext_office_file = self.config.ext_office_file

    def resolve(self, msg: MessageInfo, full_file_path: str):
        if full_file_path is None: return
        mime_type, _ = mimetypes.guess_type(full_file_path)
        file_ext = os.path.splitext(full_file_path)[1][1:]
        file_name_only = pathlib.Path(full_file_path).stem

        doc_data = cy_docs.DocumentObject(msg.Data)
        if full_file_path is None:
            return
        image_file_path = self.image_extractor_service.get_image(file_path=full_file_path)
        if image_file_path is not None:
            main_thumb_path = self.image_extractor_service.create_thumb(image_file_path, size=500)
            content_type, _ = mimetypes.guess_type(main_thumb_path)
            fs = self.file_storage_services.store_file(
                app_name=msg.AppName,
                source_file=main_thumb_path,
                rel_file_store_path=f"thumb/{doc_data.FullFileNameLower}.webp",
            )


            self.file_services.update_main_thumb_id(
                app_name=msg.AppName,
                upload_id=doc_data.id,
                main_thumb_id=fs.get_id()
            )

            if doc_data.AvailableThumbSize:
                sizes = [int(x) for x in doc_data.AvailableThumbSize.split(',') if x.strip().isnumeric()]
                available_thumbs = []
                for x in sizes:
                    self.create_thumbs(
                        app_name=msg.AppName,
                        upload_id=doc_data.id,
                        image_source_path=image_file_path,
                        scale_to_size=x

                    )
                    available_thumbs += [f"thumbs/{doc_data.id}/{x}.webp"]

                self.file_services.update_available_thumbs(
                    upload_id=doc_data.id,
                    app_name=msg.AppName,
                    available_thumbs=available_thumbs

                )
            os.remove(main_thumb_path)
        if mime_type.startswith("image/"):
            pdf_file_path = self.image_extractor_service.convert_to_pdf(file_path=full_file_path)
            ocr_file = self.pdf_services.ocr(pdf_file_path,deskew=False)
            server_orc_file_path = f"file-ocr/{doc_data.id}/{file_name_only}.pdf"
            fs = self.file_storage_services.store_file(
                app_name=msg.AppName,
                source_file=ocr_file,
                rel_file_store_path=server_orc_file_path,
            )
            self.file_services.update_ocr_info(
                app_name=msg.AppName,
                upload_id=doc_data.id,
                ocr_file_id=fs.get_id()
            )
            content, info = self.contents_services.get_text(ocr_file)
            upload_item = self.file_services.get_upload_register(
                app_name=msg.AppName,
                upload_id=doc_data.id
            )
            self.search_engine.update_content(
                app_name=msg.AppName,
                id=doc_data.id,
                content=content,
                meta=info,
                data_item=upload_item
            )
        if file_ext.lower() == "pdf":
            # try:
            print(f"OCR file {full_file_path}")
            ocr_file = self.pdf_services.ocr(full_file_path)
            if ocr_file is not None:
                print(f"OCR file {full_file_path} is ok")
                server_orc_file_path = f"file-ocr/{doc_data.id}/{file_name_only}.pdf"
                fs = self.file_storage_services.store_file(
                    app_name=msg.AppName,
                    source_file=ocr_file,
                    rel_file_store_path=server_orc_file_path,
                )
                self.file_services.update_ocr_info(
                    app_name=msg.AppName,
                    upload_id=doc_data.id,
                    ocr_file_id=fs.get_id()
                )
                content, info = self.contents_services.get_text(ocr_file)
                upload_item = self.file_services.get_upload_register(
                    app_name=msg.AppName,
                    upload_id= doc_data.id
                )
                self.search_engine.update_content(
                    app_name= msg.AppName,
                    id = doc_data.id,
                    content = content,
                    meta = info,
                    data_item = upload_item
                )



        if file_ext.lower() in self.ext_office_file and file_ext.lower()!="pdf":
            content, info = self.contents_services.get_text(full_file_path)
            upload_item = self.file_services.get_upload_register(
                app_name=msg.AppName,
                upload_id=doc_data.id
            )
            self.search_engine.update_content(
                app_name=msg.AppName,
                id=doc_data.id,
                content=content,
                meta=info,
                data_item=upload_item
            )

    def create_thumbs(self, app_name: str, upload_id: str, image_source_path: str, scale_to_size: int):

        thumb_path = self.image_extractor_service.create_thumb(image_source_path, size=scale_to_size)
        self.file_storage_services.store_file(
            app_name=app_name,
            source_file=thumb_path,
            rel_file_store_path=f"thumbs/{upload_id}/{scale_to_size}.webp",
        )
