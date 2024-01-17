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

app_admin_context = Repository.apps.app('admin')
import elasticsearch.exceptions


def get_content(resource):
    with open(resource, "rb") as fs:
        content = fs.read()
        return content.decode('utf8')


def process_pdf_content(doc_context: cy_docs.DbQueryableCollection[DocUploadRegister], doc: cy_docs.DocumentObject,
                        app_name):
    m = doc[doc_context.fields.MainFileId]
    if isinstance(m, str) and "://" in m:
        file_path = os.path.join(config.file_storage_path, m.split("://")[1])
        if not os.path.isfile(file_path):
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.SearchContentAble << False
            )

            return
        file_dir = os.path.join(pathlib.Path(file_path).parent.__str__(), "content")
        file_content_txt = os.path.join(file_dir, "content.txt")
        if os.path.isfile(file_content_txt):
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.SearchContentAble << True
            )
            try:
                search_engine.replace_content(
                    app_name=app_name,
                    id=doc.id,
                    field_value=get_content(file_content_txt),
                    field_path="content"
                )
            except elasticsearch.exceptions.NotFoundError as e:
                search_engine.make_index_content(
                    app_name=app_name,
                    upload_id=doc.id,
                    data_item=doc.to_json_convertable(),
                    privileges=doc[doc_context.fields.Privileges],
                    content=get_content(file_content_txt)

                )
                search_engine.replace_content(
                    app_name=app_name,
                    id=doc.id,
                    field_value=get_content(file_content_txt),
                    field_path="content"
                )
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.HasSearchContent << True,
                doc_context.fields.DocType << "Pdf"
            )
            return
        os.makedirs(file_dir, exist_ok=True)
        text, meta = extract_text_service.get_text(file_path)
        text = content_service.well_form_text(text)
        with open(file_content_txt, "wb") as fs:
            fs.write(text.encode('utf8'))
        try:
            search_engine.replace_content(
                app_name=app_name,
                id=doc.id,
                field_value=get_content(file_content_txt),
                field_path="content"
            )
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.HasSearchContent << True,
                doc_context.fields.DocType << "Pdf",
                doc_context.fields.IsRequireOCR << True
            )
            msg.emit(
                app_name=app_name,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT_FROM_PDF,
                data=doc.to_json_convertable(),
                resource=file_path
            )

        except elasticsearch.exceptions.NotFoundError:
            search_engine.make_index_content(
                app_name=app_name,
                upload_id=doc.id,
                data_item=doc.to_json_convertable(),
                privileges=doc[doc_context.fields.Privileges],
                content=get_content(file_content_txt)

            )
            search_engine.replace_content(
                app_name=app_name,
                id=doc.id,
                field_value=get_content(file_content_txt),
                field_path="content"
            )
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.HasSearchContent << True,
                doc_context.fields.DocType << "Pdf",
                doc_context.fields.IsRequireOCR << True
            )
            msg.emit(
                app_name=app_name,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT_FROM_PDF,
                data=doc.to_json_convertable(),
                resource=file_path
            )
        print(file_path)
    else:
        doc_context.context.update(
            doc_context.fields.id == doc.id,
            doc_context.fields.SearchContentAble << False
        )


# threading.Thread(target=do_update_doc_type_al_apps).start()
apps = app_admin_context.context.aggregate().sort(
    app_admin_context.fields.AccessCount.desc(),
    app_admin_context.fields.LatestAccess.desc()
).match(
    filter=app_admin_context.fields.Name != "admin"
)


# time.sleep(5)
def fix_pdf_doc_type(app_name):
    docs = Repository.files.app(app_name)
    items = docs.context.update(
        docs.fields.FileNameLower.endswith(".pdf"),
        docs.fields.DocType<<"Pdf"
    )


filter = (Repository.files.fields.DocType=="Pdf") & (
        (Repository.files.fields.HasSearchContent==False)|
        (Repository.files.fields.HasSearchContent==None)
)
filter = filter & (Repository.files.fields.Status==1)
filter = filter & (
        (Repository.files.fields.SearchContentAble==None)|
        (Repository.files.fields.SearchContentAble==True)
)
while True:
    for app in apps:
        fix_pdf_doc_type(app_name=app.Name)
        doc_context = Repository.files.app(app.Name)

        docs = doc_context.context.aggregate().sort(
            doc_context.fields.RegisterOn.desc()
        ).match(
            filter
        ).limit(10)
        doc_list = list(docs)
        print(f"Scan {app.Name}, {len(doc_list)}")
        for doc in docs:
            m = doc[doc_context.fields.MainFileId]
            if isinstance(m, str) and m.startswith("local://"):
                file_path = os.path.join(config.file_storage_path, m.split("://")[1])
                print(file_path)
                process_pdf_content(doc_context=doc_context, doc=doc, app_name=app.Name.lower())
            else:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.HasSearchContent << False,
                    doc_context.fields.SearchContentAble << False,
                    doc_context.fields.DocType << "Pdf"
                )

    print("xong")
    print("xong")
