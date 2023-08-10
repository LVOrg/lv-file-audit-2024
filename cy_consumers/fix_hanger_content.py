"""
Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
"""
import datetime
import os
import pathlib
import sys
import threading
import time
from datetime import timezone

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_docs
import cy_es
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.apps import AppServices

apps_service = cy_kit.singleton(AppServices)
search_engine = cy_kit.singleton(SearchEngine)

import cy_xdoc.services.files
import cyx.common.brokers

files = cy_kit.singleton(cy_xdoc.services.files.FileServices)


def fix_hanger_contents(app_name: str):

    utc_date= datetime.datetime.utcnow()- datetime.timedelta(days=1)
    broker: cyx.common.brokers.Broker = cy_kit.singleton(cyx.common.brokers.Broker)
    qr = files.get_queryable_doc(app_name=app_name)
    lst = qr.context.aggregate() \
        .match(
        (qr.fields.RegisterOn <= utc_date) & \
        (qr.fields.Status == 0) & \
        cy_docs.EXPR(qr.fields.SizeInBytes == qr.fields.SizeUploaded)
    ) \
        .sort(qr.fields.RegisterOn.desc()).to_json_convertable()
    lst = list(lst)
    print(f"{app_name} found {len(lst)}")
    for x in lst:
        qr.context.update(
            qr.fields.id == x._id,
            qr.fields.Status << 1
        )
        broker.emit(
            app_name=app_name,
            message_type=cyx.common.msg.MSG_FILE_UPLOAD,
            data=x
        )


import elasticsearch

if __name__ == "__main__":
    while True:
        apps = apps_service.get_list(app_name='admin')
        ths = []
        for x in apps:
            print(f"Process {x['Name']}")
            try:
                fix_hanger_contents(x["Name"])
            except Exception as e:
                print(e)
        time.sleep(24*69*60)
