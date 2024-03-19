# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_generate_image_from_office.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672 debug=1
import os.path
import pathlib
import sys
import uuid

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
sys.path.append("/app")
import cy_file_cryptor.wrappers
import cyx.framewwork_configs
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)
msg = cy_kit.singleton(RabitmqMsg)


if sys.platform == "linux":
    import signal

    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

from cyx.common.msg import broker
from cyx.loggers import LoggerService
from cyx.content_services import ContentService,ContentTypeEnum
from cyx.media.libre_office import LibreOfficeService
from cy_xdoc.services.files import FileServices
from cyx.content_services import ContentService,ContentTypeEnum
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.mongo_db_services import MongodbService
from cyx.common import config
from cyx.local_api_services import LocalAPIService
@broker(message=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE)
class Process:
    def __init__(self,
                 logger=cy_kit.singleton(LoggerService),
                 content_service= cy_kit.singleton(ContentService),
                 libre_office_service=cy_kit.singleton(LibreOfficeService),
                 mongodb_service=cy_kit.singleton(MongodbService),
                 local_api_service: LocalAPIService = cy_kit.singleton(LocalAPIService),
                 temp_file=cy_kit.singleton(TempFiles),
                 ):
        self.logger = logger
        self.content_service=content_service
        self.libre_office_service=libre_office_service
        self.mongodb_service=mongodb_service
        self.local_api_service=local_api_service
        self.temp_file = temp_file

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        try:
            rel_file_path = msg_info.Data["MainFileId"].split("://")[1]

            server_file = config.private_web_api + "/api/sys/admin/content-share/" + rel_file_path
            if not msg_info.Data.get("local_share_id"):
                msg.delete(msg_info)
                return
            local_share_id = msg_info.Data["local_share_id"]
            server_file += f"?local-share-id={local_share_id}&app-name={msg_info.AppName}"
            if not os.path.isdir(self.temp_file.get_root_dir()):
                os.makedirs(self.temp_file.get_root_dir(), exist_ok=True)
            file_path = os.path.join(self.temp_file.get_root_dir(),str(uuid.uuid4()))
            with open(server_file,"rb") as fs:
                data = fs.read()
                with open(file_path,"wb") as f:
                    f.write(data)
            main_file_id=msg_info.Data["MainFileId"]
            server_dir = pathlib.Path(main_file_id.split("://")[1]).parent.__str__().replace(os.sep, '/')
            rel_server_path = os.path.join(server_dir, pathlib.Path(main_file_id).name + ".png").replace(os.sep, '/')
            image_file_path=self.libre_office_service.get_image(file_path=file_path)
            self.local_api_service.send_file(
                file_path=image_file_path,
                token=None,
                local_share_id=local_share_id,
                app_name=msg_info.AppName,
                rel_server_path=rel_server_path

            )
            print(server_file)
            os.remove(file_path)
            os.remove(image_file_path)
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data,
                parent_msg=msg_info.MsgType,
                parent_tag=msg_info.tags["method"].delivery_tag,
                resource= rel_server_path,
                require_tracking=True

            )
            msg.delete(msg_info)
        except:
            pass
        # try:
        #
        #     # resource = self.content_service.get_resource(msg_info)+rel_file_path
        # #     if resource is None:
        # #         raise Exception("No")
        # #     print(f"{msg_info.MsgType} of {resource}")
        # #     img_file = self.libre_office_service.get_image(file_path=resource)
        # #     if not os.path.isfile(img_file):
        # #         raise  FileNotFoundError()

        # #     msg.delete(msg_info)
        # except Exception as ex:
        #     print(ex)
        # except:
        #     docs = self.mongodb_service.db(msg_info.AppName).get_document_context(DocUploadRegister)
        #     docs.context.update(
        #         docs.fields.id==msg_info.Data["_id"],
        #         docs.fields.ThumbnailsAble<<False
        #     )
        #     # msg.delete(msg_info)


    def on_receive_msg_delete(self, msg_info: MessageInfo, msg_broker: MessageService):
        from cyx.media.libre_office import LibreOfficeService
        libre_office_service = cy_kit.singleton(LibreOfficeService)
        ext_file = msg_info.Data.get("FileExt")
        if ext_file is None:
            ext_file = pathlib.Path(msg_info.Data["FileName"]).suffix
            if ext_file:
                ext_file = ext_file[1:].lower()
        if ext_file == "pdf":
            msg.delete(msg_info)
            return
        full_file = msg_info.Data.get("processing_file")
        if not full_file:
            if isinstance(msg_info.Data.get("MainFileId"),str):
                full_file = os.path.join(cyx.common.config.file_storage_path, msg_info.Data.get("MainFileId").split("://")[1])
                if not os.path.isfile(full_file):
                    full_file = None
        if not full_file:
            full_file = temp_file.get_path(
                app_name=msg_info.AppName,
                file_ext=msg_info.Data["FileExt"],
                upload_id=msg_info.Data["_id"],
                file_id=msg_info.Data.get("MainFileId")

            )
        if full_file is None:
            self.logger.info(f"Generate image form nothing")
            msg.delete(msg_info)
            return
        if not os.path.isfile(full_file):
            self.logger.info(f"Generate image form nothing")
            msg.delete(msg_info)
            return

        self.logger.info(f"Generate image form {full_file}")
        self.logger.info(f"Generate image form {full_file} start")
        img_file = libre_office_service.get_image(file_path=full_file)
        self.logger.info(f"Generate image form {full_file} end")
        # ret = temp_file.move_file(
        #     from_file=img_file,
        #     app_name=msg_info.AppName,
        #     sub_dir=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF
        # )
        msg_info.Data["processing_file"] = img_file
        msg.emit(
            app_name=msg_info.AppName,
            message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
            data=msg_info.Data
        )
        self.logger.info(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n {full_file}")
        msg.delete(msg_info)
        self.logger.info(msg_info.Data)