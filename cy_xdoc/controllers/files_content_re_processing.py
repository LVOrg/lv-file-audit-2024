import mimetypes
import typing

import humanize

import cy_docs
import cy_web
import cyx.common.msg
from cy_xdoc.auths import Authenticate
from fastapi import Depends, UploadFile
from cy_xdoc.controllers.models.file_upload import UploadFilesChunkInfoResult
import cy_kit
from cy_xdoc.services.files import FileServices
from cyx.common.file_storage import FileStorageService
from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker
import fastapi
import cy_xdoc
@cy_web.hanlder("post", "{app_name}/files/content-re-process")
def files_upload(app_name: str, UploadIds: typing.List[str],
                 token=fastapi.Depends(cy_xdoc.auths.Authenticate)):
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    ret= []
    file_service: FileServices = cy_kit.singleton(FileServices)
    file_storage_service: FileStorageService = cy_kit.singleton(FileStorageService)
    msg_service: MessageService = cy_kit.singleton(MessageService)
    broker:Broker = cy_kit.singleton(Broker)
    temp_files = cy_kit.singleton(TempFiles)
    for UploadId in UploadIds:
        upload_item = file_service.get_upload_register(app_name, upload_id=UploadId)
        if upload_item:
            try:
                broker.emit(
                    app_name=app_name,
                    message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                    data=upload_item
                )
                ret += [{
                    "UploadId": UploadId,
                    "Message": "Is in processing"
                }]
                print(f"rais msg {cyx.common.msg.MSG_FILE_UPLOAD}")
            except Exception as e:
                ret += [{
                    "UploadId": UploadId,
                    "Message": "Error broker"
                }]

        else:
            ret += [{
                "UploadId": UploadId,
                "Message": "Content was not found"
            }]

    return ret