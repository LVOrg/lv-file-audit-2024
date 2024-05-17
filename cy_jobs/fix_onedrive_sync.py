import os.path
import pathlib
import sys

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import json
import time

import cy_docs
from cyx.common import config
from cyx.repository import Repository

from cy_jobs.cy_job_libs import JobLibs
from cyx.rabbit_utils import Consumer, MesssageBlock
import cyx.common.msg

apps = Repository.apps.app("admin").context.aggregate().match(
    (Repository.apps.fields.AppOnCloud.Azure.ClientSecret != None) | (
                Repository.apps.fields.AppOnCloud.Google.ClientSecret != None)
).project(
    cy_docs.fields.app_name >> Repository.apps.fields.Name
)
ms_consumer = Consumer(cyx.common.msg.MSG_CLOUD_ONE_DRIVE_SYNC)
gg_consumer = Consumer(cyx.common.msg.MSG_CLOUD_GOOGLE_DRIVE_SYNC)


def do_fix(app_name):
    google_filter = (Repository.files.fields.StorageType == "google-drive")
    azure_filter = Repository.files.fields.StorageType == "onedrive"

    filter = (((Repository.files.fields.CloudId == None)&(Repository.files.fields.LossContentFile!=True)) &
              (azure_filter))

    files = Repository.files.app(app_name).context.aggregate().sort(
        Repository.files.fields.cloud_sync_time.asc(),
        Repository.files.fields.RegisterOn.desc()
    ).match(
        filter
    ).limit(10)
    for file in files:
        server_file, rel_file_path, download_file_path, token, local_share_id = JobLibs.local_api_service.get_download_path(
            file, app_name=app_name)
        full_path = os.path.join("/mnt/files", rel_file_path)
        if not os.path.isfile(full_path):
            Repository.files.app(app_name).context.update(
                Repository.files.fields.id == file.Id,
                Repository.files.fields.LossContentFile << True
            )
            continue

        print(full_path)
        msg = MesssageBlock()
        msg.data =file.to_json_convertable()
        msg.app_name= app_name
        ms_consumer.resume(msg)
        print("X")
        # if file[Repository.files.fields.StorageType]=="google-drive":
        #     gg_consumer.resume(msg)
        # if file[Repository.files.fields.StorageType]=="onedrive":
        #     ms_consumer.resume(msg)
        #
        # txt=json.dumps(file.to_json_convertable(),indent=4)
        # print(txt)


while True:
    for app_item in apps:
        token_info, error = JobLibs.azure_utils_services.acquire_token(app_item.app_name, True)
        if not error:
            do_fix(app_item.app_name)
    time.sleep(0.5)
