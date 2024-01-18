import pathlib
import shutil
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cyx.framewwork_configs
import cy_docs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common import config
from cyx.media.pdf import PDFService
from cyx.media.image_extractor import ImageExtractorService

from cyx.common.rabitmq_message import RabitmqMsg

msg = cy_kit.singleton(RabitmqMsg)
from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.apps import App
from cyx.content_services import ContentService, ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.media.contents import ContentsServices
import os
from cy_xdoc.services.search_engine import SearchEngine

search_engine: SearchEngine = cy_kit.singleton(SearchEngine)
file_services = cy_kit.singleton(FileServices)
content_service = cy_kit.singleton(ContentService)
mongodb_service: MongodbService = cy_kit.singleton(MongodbService)
extract_text_service = cy_kit.singleton(ContentsServices)
logger = cy_kit.singleton(LoggerService)
from cyx.repository import Repository
from cyx.common import config
from cyx.ocr_vietocr_utils import ocr_content
app_admin_context = Repository.apps.app('admin')
import elasticsearch.exceptions


def get_content(resource):
    with open(resource, "rb") as fs:
        content = fs.read()
        return content.decode('utf8')
# threading.Thread(target=do_update_doc_type_al_apps).start()
apps = app_admin_context.context.aggregate().sort(
    app_admin_context.fields.AccessCount.desc(),
    app_admin_context.fields.LatestAccess.desc()
).match(
    filter=app_admin_context.fields.Name != "admin"
)


# time.sleep(5)


filter = (Repository.files.fields.MimeType.startswith("image/")) & (
        (Repository.files.fields.HasORCContentV2==False)|
        (Repository.files.fields.HasORCContentV2==None)
)
filter = filter & (Repository.files.fields.Status==1)
import cv2

def update_content_search(app_name:str, id:str,content:str):
    files = Repository.files.app(app_name)
    doc = files.context @ id
    if doc:
        try:
            search_engine.replace_content(
                app_name=app_name,
                id=doc.id,
                field_value=content,
                field_path="content",
                timeout="30s"
            )
        except elasticsearch.exceptions.NotFoundError as e:
            search_engine.make_index_content(
                app_name=app_name,
                upload_id=doc.id,
                data_item=doc.to_json_convertable(),
                privileges=doc[doc_context.fields.Privileges],
                content=content

            )
            search_engine.replace_content(
                app_name=app_name,
                id=doc.id,
                field_value=content,
                field_path="content"
            )
        files.context.update(
            files.fields.id==id,
            files.fields.HasORCContentV2<<True
        )

while True:
    for app in apps:
        doc_context = Repository.files.app(app.Name)

        docs = doc_context.context.aggregate().sort(
            doc_context.fields.RegisterOn.desc()
        ).match(
            filter
        ).limit(1)
        doc_list = list(docs)
        print(f"Scan {app.Name}, {len(doc_list)}")
        for doc in docs:
            try:
                m = doc[doc_context.fields.MainFileId]
                if isinstance(m, str) and m.startswith("local://"):
                    file_path = os.path.join(config.file_storage_path, m.split("://")[1])
                    if not os.path.isfile(file_path):
                        print(f"Not found (skip) {file_path}")
                        continue
                    print(f"Porcessing ... {file_path}")
                    ocr_job_dir = os.path.join(pathlib.Path(file_path).parent.__str__(), "ocr-job-v2")
                    os.makedirs(ocr_job_dir, exist_ok=True)
                    ocr_content_job_file_path = os.path.join(ocr_job_dir, "content.txt")
                    if not os.path.isfile(ocr_content_job_file_path):
                        txt = ocr_content.ocr_image(file_path)
                        with open(ocr_content_job_file_path,"w",encoding="utf-8") as fs:
                            fs.write(txt)
                    else:
                        with open(ocr_content_job_file_path,"r",encoding="utf-8") as fs:
                            txt = fs.read()
                    txt = content_service.well_form_text(txt)
                    update_content_search(app_name=app.Name,id=doc.id,content=txt)
                    # process_pdf_content(doc_context=doc_context, doc=doc, app_name=app.Name.lower())
            except cv2.error:
                doc_context.context.update(
                    doc_context.fields.id==doc.id,
                    doc_context.fields.HasORCContentV2<<True,
                    doc_context.fields.SearchContentAble << False,
                )
            except ValueError:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.HasORCContent << True,
                    doc_context.fields.SearchContentAble << False,
                )
    print("xong")
    print("xong")
