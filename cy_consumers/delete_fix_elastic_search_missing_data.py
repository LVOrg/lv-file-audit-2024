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


def fix_error(data_privileges):
    """
    Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
    :param data_privileges:
    :return:
    """
    if isinstance(data_privileges, dict):
        for k, v in data_privileges.items():
            if isinstance(v, list):
                t = []
                for x in v:
                    if x == "":
                        t += ["."]
                    else:
                        t += ["x"]
                data_privileges[k] = t

    elif isinstance(data_privileges, list):
        return [fix_error(x) for x in data_privileges]
    else:
        return data_privileges
    return data_privileges

import cy_xdoc.services.files
files = cy_kit.singleton(cy_xdoc.services.files.FileServices)


def fix_privilges_error(data_privileges):
    """
    Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
    :param data_privileges:
    :return:
    """
    if isinstance(data_privileges, dict):
        for k, v in data_privileges.items():
            if isinstance(v, list):
                t = []
                for x in v:
                    if x == "." or x== 0:
                        t += [""]
                    else:
                        t+=[x]

                data_privileges[k] = t

    elif isinstance(data_privileges, list):
        return [fix_privilges_error(x) for x in data_privileges]
    else:
        return data_privileges
    return data_privileges
def fix_app(app_name: str):
    utc_date = datetime.datetime(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day, 23, 59, 59, 999, tzinfo=timezone.utc)
    qr = files.get_queryable_doc(app_name=app_name)


    page_index = 0
    page_size = 20
    lst = qr.context.aggregate().match(
        qr.fields.RegisterOn<=utc_date
    ).sort(qr.fields.RegisterOn.desc()).skip(page_size*page_index).limit(page_size).project(
        qr.fields.Privileges,
        qr.fields.id
    ).to_json_convertable()
    lst = list(lst)
    print(app_name)
    while lst.__len__()>0:
        for x in lst:
            if x["Privileges"]!={}:
                privileges = x["Privileges"]
                print(f"{app_name}-- {privileges}")
                print(f"------------{app_name}-------fix----------------")
                privileges = fix_privilges_error(privileges)

                print(f"{app_name}-- {privileges}")
                print(x["_id"])
                try:
                    search_engine.create_or_update_privileges(
                        app_name=app_name,
                        privileges=privileges,
                        data_item=None,
                        upload_id=x["_id"]
                    )
                    print(f'{app_name} fix error data of {x["_id"]} ok')
                except  Exception as e:
                    print(f'{app_name} fix error data of {x["_id"]} error')
                    print(e)
        page_index+=1
        lst = qr.context.aggregate().match(
            qr.fields.RegisterOn <= utc_date
        ).sort(qr.fields.RegisterOn.desc()).skip(page_size * page_index).limit(page_size).project(
            qr.fields.Privileges,
            qr.fields.id
        ).to_json_convertable()
        lst = list(lst)

import elasticsearch
if __name__ == "__main__":
    apps = apps_service.get_list(app_name='admin')
    ths = []
    for x in apps:
        print(f"Process {x['Name']}")
        try:
            fix_app(x["Name"])
        except Exception  as e:
            print(e)

    print("XONG")