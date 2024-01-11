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
app_admin_context = mongodb_service.db("admin").get_document_context(App)
import elasticsearch.exceptions

def get_content(resource):
    with open(resource, "rb") as fs:
        content = fs.read()
        return content.decode('utf8')
def process_office_content(doc_context:cy_docs.DbQueryableCollection[DocUploadRegister], doc:cy_docs.DocumentObject, app_name):
    m=doc[doc_context.fields.MainFileId]
    if isinstance(m,str) and "://" in m:
        file_path = os.path.join(config.file_storage_path,m.split("://")[1])
        if not os.path.isfile(file_path):
            doc_context.context.update(
                doc_context.fields.id == doc.id,
                doc_context.fields.SearchContentAble << False
            )

            return
        file_dir = os.path.join(pathlib.Path(file_path).parent.__str__(),"content")
        file_content_txt = os.path.join(file_dir,"content.txt")
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
                doc_context.fields.DocType<<"Office"
            )
            return
        os.makedirs(file_dir,exist_ok=True)
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
                doc_context.fields.DocType<<"Office"
            )
            time.sleep(0.3)
        except Exception as e:
            raise e
        print(file_path)
    else:
        doc_context.context.update(
            doc_context.fields.id == doc.id,
            doc_context.fields.SearchContentAble << False
        )


def do_update_doc_type(doc_context: cy_docs.DbQueryableCollection[DocUploadRegister]):
    docs = doc_context.context.find(
        (cy_docs.not_exists(doc_context.fields.DocType)),
        linmit=10
    )
    list_docs = list(docs)
    print(f"found {len(list_docs)}")
    while len(list_docs) > 0:
        for doc in list_docs:
            fx = content_service.get_type(doc.to_json_convertable())
            if fx == ContentTypeEnum.Unknown:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.SearchContentAble << False,
                    doc_context.fields.DocType << "Unknown"
                )
                continue
            if fx == ContentTypeEnum.Office:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.SearchContentAble << True,
                    doc_context.fields.DocType << "Office"
                )
                continue
            if fx == ContentTypeEnum.Pdf:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.SearchContentAble << True,
                    doc_context.fields.DocType << "Pdf"
                )
                continue
            if fx == ContentTypeEnum.Video:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.SearchContentAble << True,
                    doc_context.fields.DocType << "Video"
                )
                continue
            if fx == ContentTypeEnum.Image:
                doc_context.context.update(
                    doc_context.fields.id == doc.id,
                    doc_context.fields.SearchContentAble << True,
                    doc_context.fields.DocType << "Image"
                )
                continue
        docs = doc_context.context.find(
            (cy_docs.not_exists(doc_context.fields.DocType)),
            linmit=10
        )
        list_docs = list(docs)


def do_update_doc_type_al_apps():
    apps = app_admin_context.context.aggregate().sort(
        app_admin_context.fields.RegisteredOn.desc()
    ).match(
        filter=app_admin_context.fields.Name == "qtscdemo"
    ).limit(10)

    for app in apps:
        doc_context = mongodb_service.db(app.Name.lower()).get_document_context(DocUploadRegister)
        do_update_doc_type(doc_context)


threading.Thread(target=do_update_doc_type_al_apps).start()
apps = app_admin_context.context.aggregate().sort(
    app_admin_context.fields.AccessCount.desc(),
    app_admin_context.fields.LatestAccess.desc()
).match(
    filter=app_admin_context.fields.Name != "admin"
)
# time.sleep(5)
while True:
    for app in apps:
        try:
            doc_context = mongodb_service.db(app.Name.lower()).get_document_context(DocUploadRegister)
            filter = ((doc_context.fields.DocType=="Office")&
                      (cy_docs.not_exists(doc_context.fields.HasSearchContent) |
                       (doc_context.fields.HasSearchContent==False)))
            filter = filter & ((doc_context.fields.SearchContentAble==True)|(cy_docs.not_exists(doc_context.fields.SearchContentAble)))

            filter= filter & (doc_context.fields.Status==1)
            docs = doc_context.context.aggregate().sort(
                doc_context.fields.RegisterOn.desc()
            ).match(
                filter
            ).limit(10)
            doc_list= list(docs)
            print(f"Scan {app.Name}, {len(doc_list)}")
            while len(doc_list)>0:
                for doc in docs:
                    m = doc[doc_context.fields.MainFileId]
                    if isinstance(m, str) and "://" in m:
                        file_path = os.path.join(config.file_storage_path, m.split("://")[1])
                        print(file_path)
                        fx = content_service.get_type(doc.to_json_convertable())
                        if fx == ContentTypeEnum.Office:
                            try:
                                process_office_content(doc_context=doc_context, doc=doc, app_name=app.Name.lower())
                            except Exception as e:
                                print(e)
                                continue

                        print(doc[doc_context.fields.MainFileId])


        except Exception as e:
            print(e)
        print("xong")
    print("xong")
