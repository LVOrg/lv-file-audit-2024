from torch.distributed.autograd import context

import cy_docs
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.msg_mongodb import MessageServiceMongodb
from cyx.common.rabitmq_message import RabitmqMsg
fs:FileServices = cy_kit.singleton(FileServices)
msg =cy_kit.singleton(RabitmqMsg)
app_name = "hps-file-test"

context = fs.db_connect.db(app_name).doc(DocUploadRegister)

lst = context.context.aggregate().match(
    # {
    #     "_id":"76f925ee-452a-42b6-8a8c-9300a0bc1f70"
    # }
    ((context.fields.Status==1)&(context.fields.FileExt=="mp4"))



).sort(
    context.fields.RegisterOn.desc()
).limit(100)

for x in lst:
    msg.emit(
        app_name=app_name,
        data= x,
        message_type='files.upload'
    )

    print(x)