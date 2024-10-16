# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_pdf_from_image.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import pathlib
import sys
working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import PIL
import bson
import img2pdf


import os.path
import pathlib

import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
from cyx.common.temp_file import TempFiles
from cyx.easy_ocr import EasyOCRService


temp_file = cy_kit.singleton(TempFiles)

msg = cy_kit.singleton(RabitmqMsg)













from cyx.loggers import LoggerService
from cyx.common.msg import broker
@broker(message=cyx.common.msg.MSG_FILE_MOVE_TENANT)
class Process:
    def __init__(self,
                 logger = cy_kit.singleton(LoggerService)
                 ):
        self.logger = logger

    def do_move(self,from_app, to_app, ids):
        from cy_xdoc.services.files import FileServices
        from cyx.common.file_storage_mongodb import MongoDbFileStorage
        tmp_file = cy_kit.singleton(TempFiles)
        files = cy_kit.singleton(FileServices)
        fs = cy_kit.singleton(MongoDbFileStorage)
        db_context = files.get_queryable_doc(from_app).context
        db_context_to = files.get_queryable_doc(to_app).context
        root_dir = tmp_file.get_root_dir()
        tmp_move_file = os.path.join(root_dir, "tmp_move_tenant")
        if not os.path.isdir(tmp_move_file):
            os.makedirs(tmp_move_file, exist_ok=True)
        for id in ids:
            data_item = db_context @ id
            if not data_item:
                continue
            file_name = data_item.FileName

            file = fs.get_file_by_id(
                from_app,
                id=data_item.MainFileId
            )
            size_of_file = file.fs.length

            to_data_item = db_context_to @ id
            if to_data_item:
                db_context_to.delete({"_id": id})
            fs.delete_files(
                app_name=to_app,
                files=[data_item.FullFileNameLower],
                run_in_thread=False
            )
            new_file = fs.create(
                app_name=to_app,
                chunk_size=data_item.ChunkSizeInBytes,
                rel_file_path=data_item.FullFileNameLower,
                content_type=data_item.MimeType,
                size=size_of_file

            )
            content = file.read(data_item.ChunkSizeInBytes)
            chunk_index = 0
            while content.__len__() > 0:
                new_file.push(
                    content=content,
                    chunk_index=chunk_index

                )
                chunk_index += 1
                content = file.read(data_item.ChunkSizeInBytes)
            data_item.MainFileId = bson.ObjectId(new_file.get_id())
            data_item.HasThumb = False
            data_item.pop('OCRFileId')
            data_item.pop('ThumbFileId')
            data_item.pop('AvailableThumbs')
            db_context_to.insert_one(data_item)
            upload_item = files.get_upload_register(to_app, upload_id=id)
            msg.emit(
                app_name=to_app,
                message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                data=upload_item
            )
            self.logger.info (data_item)

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            from_app = msg_info.Data["from_app"]
            to_app = msg_info.Data["to_app"]
            ids = msg_info.Data["ids"]
            self.do_move(from_app=from_app, to_app=to_app, ids=ids)
        except Exception as e:
            self.logger.error(e,msg_info=dict(from_app=from_app, to_app=to_app, ids=ids))
