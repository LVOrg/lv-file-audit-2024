import pathlib
import sys
import time

from icecream import ic

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
from cyx.common import config
if not hasattr(config,"msg_ocr"):
    raise Exception(f"msg_ocr was not found in config")
if not hasattr(config,"app_name"):
    raise Exception(f"app_name was not found in config")
msg_raise_ocr:str = config.msg_ocr
"""
Message wil be raise 
"""

import cy_docs
from cyx.rabbit_utils import Consumer
from cyx.repository import Repository
consumer = Consumer(msg_raise_ocr)
def get_qr_by_tenant(tenant_name:str):
    agg_ocr_file = (Repository.files.app(tenant_name).context.aggregate().match(
      Repository.files.fields.Status==1
    ).match(
        Repository.files.fields.FileExt=="pdf"
    ).match(
        ((Repository.files.fields.MsgOCRReRaise ==None)|(Repository.files.fields.MsgOCRReRaise!=msg_raise_ocr))
    ).sort(
        Repository.files.fields.RegisterOn.desc()
    ).project(
        cy_docs.fields.upload_id>>Repository.files.fields.id
    )).limit(1)
    return agg_ocr_file
def get_app_name_list():
    app_names = Repository.apps.app("admin").context.aggregate().match(
        Repository.apps.fields.Name!="admin"
    ).project(
        cy_docs.fields.app_name>> Repository.apps.fields.NameLower
    )
    return app_names
def run_producer(tenant_name:str):
    agg_ocr_file = get_qr_by_tenant(tenant_name)
    ic(agg_ocr_file)
    for x in agg_ocr_file:
        ic(f"tenant={tenant_name} {x}")
        data = Repository.files.app(tenant_name).context.find_one(
            Repository.files.fields.id ==x.upload_id
        )
        if not data:
            continue
        data =data.to_json_convertable()
        consumer.raise_message(
            app_name=tenant_name,
            data =data,
            msg_type=msg_raise_ocr
        )
        Repository.files.app(tenant_name).context.update(
            Repository.files.fields.id == x.upload_id,
            Repository.files.fields.MsgOCRReRaise<<msg_raise_ocr
        )
        ic(f"{tenant_name} with id={x.upload_id} was raise")
def main():
    while True:
        for app in get_app_name_list():
            tenant_name = app.app_name
            try:
                run_producer(tenant_name)
            except:
                continue
        time.sleep(1)
if __name__ == "__main__":
    main()