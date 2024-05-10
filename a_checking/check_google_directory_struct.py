import cy_docs
import cy_kit
from cyx.g_drive_services import GDriveService
from cyx.cloud.drive_services import DriveService
from cyx.repository import Repository
from cyx.google_drive_utils.directories import GoogleDirectoryService
context = Repository.files.app("lv-docs")
lst = g_files = context.context.aggregate().sort(
    Repository.files.fields.RegisterOn.desc()
).match(
    Repository.files.fields.CloudId!=None
).project(
    cy_docs.fields.CloudId>>Repository.files.fields.CloudId
)
lst=list(lst)


g:GoogleDirectoryService= cy_kit.singleton(GoogleDirectoryService)
fx,list_of_folder,error= g.get_all_folders("lv-docs")
# g.check_folder_structure("lv-docs","Long-test/2024/09")
for x in lst:
    url =g.get_thumbnail_url_by_file_id(app_name="lv-docs",file_id=x.CloudId)
    print(url)
