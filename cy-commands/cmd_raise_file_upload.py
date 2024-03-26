import pathlib

import cy_xdoc.services.files
import cyx.common.brokers

working_dir = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(working_dir)
import cy_kit
file_services = cy_kit.singleton(cy_xdoc.services.files.FileServices)
broker:cyx.common.brokers.Broker = cy_kit.singleton(cyx.common.brokers.Broker)
app_name="hps-file-test"
docs = file_services.get_queryable_doc(
    app_name=app_name,
)
items =docs.context.find(
    filter= docs.fields.HasThumb==False,
    linmit=100
)
for x in items:
    print(x)
    broker.emit(
        app_name=app_name,
        message_type=cyx.common.msg.MSG_FILE_UPLOAD,
        data=x
    )

