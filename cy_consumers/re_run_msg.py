import sys
sys.path.append("/home/vmadmin/python/v6/file-service-02")
import cy_docs

from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.apps import AppServices
import cyx.common.msg
import cy_kit
# cy_kit.config_provider(
#         from_class=MessageService,
#         implement_class=RabitmqMsg
#     )

msg = cy_kit.singleton(RabitmqMsg)
files = cy_kit.singleton(FileServices)
apps = cy_kit.singleton(AppServices)
apps_list = apps.get_list("admin")
for app in apps_list:
    # if app.Name not in ["default"]:
    #     continue
    qr = files.get_queryable_doc(app.Name)
    items = qr.context.aggregate().match(
        ((qr.fields.HasThumb == False) | (cy_docs.not_exists(qr.fields.HasThumb))) & \
        (cy_docs.EXPR(qr.fields.SizeInBytes ==qr.fields.SizeUploaded))
    ).sort(
        qr.fields.RegisterOn.desc()
    ).limit(500)
    for x in items:
        print(f"{app.Name}\t{x[qr.fields.FileName]}")
        msg.emit(
            app_name=app.Name,
            message_type=cyx.common.msg.MSG_FILE_UPLOAD,
            data=x
        )

