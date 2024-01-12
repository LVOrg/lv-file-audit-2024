import os.path
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
import elasticsearch


from cyx.repository import Repository
from cyx.content_services import ContentService,ContentTypeEnum


content_service = cy_kit.singleton(ContentService)
from cyx.easy_ocr import EasyOCRService
easy_ocr_service= cy_kit.singleton(EasyOCRService)
from cyx.common import config

from cy_xdoc.services.search_engine import SearchEngine
search_engine: SearchEngine = cy_kit.singleton(SearchEngine)

def read_content(content_file):
    with open(content_file,"rb") as fs:
        ret=fs.read().decode("utf8")
        return ret


def save_content(content_file, contents:str):
    with open(content_file, "wb") as fs:
        fs.write(contents.encode("utf8"))
apps = Repository.apps.app("admin").context.aggregate().sort(
    Repository.apps.fields.LatestAccess.desc()
).match(
    Repository.apps.fields.Name!="admin"
)
for app in apps:
    try:
        app_name= app.Name
        print(f"{app_name}...")
        Repository.files.app(app_name).context.update(
            Repository.files.fields.MimeType.startswith("image/"),
            Repository.files.fields.DocType<<"Image"
        )
        items = Repository.files.app(app_name).context.aggregate().sort(
            Repository.files.fields.RegisterOn.desc()
        ).match(
            Repository.files.fields.MimeType.startswith("image/")&(
                (Repository.files.fields.HasSearchContent == None)|(Repository.files.fields.HasSearchContent == False)
            )&(
                Repository.files.fields.MainFileId.__contains__("://")
            )
        ).limit(10)
        list_items = list(items)
        while len(list_items)>0:
            for x in items:
                resource= x[Repository.files.fields.MainFileId]
                if resource is None:
                    continue
                if not isinstance(resource,str):
                    continue
                if "://" in resource:
                    resource= os.path.join(config.file_storage_path,resource.split("://")[1])
                    if not os.path.isfile(resource):
                        continue
                    content_dir= os.path.join(pathlib.Path(resource).parent.__str__(),"content")
                    if not os.path.isdir(content_dir):
                        os.makedirs(content_dir,exist_ok=True)
                    content_file = os.path.join(content_dir,"content.txt")
                    if os.path.isfile(content_file):
                        contents = read_content(content_file)
                    else:
                        contents= easy_ocr_service.get_text(resource)
                        contents = content_service.well_form_text(contents)
                    save_content(content_file,contents)
                    try:
                        search_engine.replace_content(
                            app_name=app_name,
                            id=x.id,
                            field_value=contents,
                            field_path="content",
                            timeout="30s"
                        )
                    except elasticsearch.exceptions.NotFoundError as e:
                        search_engine.make_index_content(
                            app_name=app_name,
                            upload_id=x.id,
                            data_item=x.to_json_convertable(),
                            privileges=x[Repository.files.fields.Privileges],
                            content=contents

                        )
                        search_engine.replace_content(
                            app_name=app_name,
                            id=x.id,
                            field_value=contents,
                            field_path="content"
                        )
                    Repository.files.app(app_name).context.update(
                        Repository.files.fields.id==x.id,
                        Repository.files.fields.SearchContentAble<<True,
                        Repository.files.fields.HasSearchContent<<True
                    )
                print(x)
            items = Repository.files.app(app_name).context.aggregate().sort(
                Repository.files.fields.RegisterOn.desc()
            ).match(
                Repository.files.fields.MimeType.startswith("image/") & (
                        (Repository.files.fields.HasSearchContent == None) | (
                            Repository.files.fields.HasSearchContent == False)
                )
            ).limit(10)
            list_items = list(items)
        print(f"{app_name} finish")
    except Exception as e:
        print(e)
        continue