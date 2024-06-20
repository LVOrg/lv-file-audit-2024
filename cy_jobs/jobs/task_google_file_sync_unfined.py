import cy_docs
from cyx.repository import Repository
from cyx.rabbit_utils import Consumer
import cyx.common.msg
consumer = Consumer(cyx.common.msg.MSG_CLOUD_GOOGLE_DRIVE_SYNC)
apps = Repository.apps.app("admin").context.aggregate().match(
    Repository.apps.fields.AppOnCloud.Google.ClientSecret!=None
).project(
    cy_docs.fields.app_name>>Repository.apps.fields.Name
)
for app in apps:
    app_name=app.app_name
    files = Repository.files.app(app_name).context.find(
        filter=      (Repository.files.fields.FullPathOnCloud!=None) & (Repository.files.fields.google_file_id==None)
    )
    for x in files:
        print(x[Repository.files.fields.FullPathOnCloud])
        consumer.raise_message(app_name=app_name,data=x.to_json_convertable())

