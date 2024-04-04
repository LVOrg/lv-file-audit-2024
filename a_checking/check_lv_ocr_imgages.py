import cy_docs
from cyx.repository import Repository
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common import config
import cyx.common.msg
import cy_kit
msg = cy_kit.singleton(RabitmqMsg)
apps = Repository.apps.app("admin").context.find({})
finish = dict()
_apps = list(apps)
while len(list(finish.keys()))<len(_apps):
    for app in _apps:
        if finish.get(app.Name):
            continue
        files_context = Repository.files.app(app.Name)
        files = files_context.context.aggregate().match(
            files_context.fields.MimeType.startswith("image/") & (files_context.fields.IsLvOrc==None)
        ).sort(
            files_context.fields.RegisterOn.desc()
        ).limit(10)
        total = 0
        for item in files:
            msg.emit(
                app_name=app.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_CONTENT_FROM_IMAGE,
                require_tracking=True,
                data=item.to_json_convertable()

            )
            files_context.context.update(
                files_context.fields.id==item.id,
                files_context.fields.IsLvOrc<<True
            )
            total+=1
        print(f"app={app.Name}, count={total}")
        if total==0:
            finish[app.Name] = app.Name
print("Xong")


