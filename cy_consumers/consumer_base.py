import os.path
import pathlib
import sys
import typing

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cyx.common.msg

from cy_xdoc.models.files import DocUploadRegister
import cyx.base

__app_path__ = pathlib.Path(__file__).parent.parent.__str__()
class BaseConsumer:
    def docs(self, app_name: str) -> cyx.base.DbCollection[DocUploadRegister]:
        ret = self.db_connect.db(app_name).doc(DocUploadRegister)
        return ret

    def __init__(self, file_path):
        self.temp_path = os.path.join(__app_path__,"share-storage","tmp-file-processing","tmp")
        if not os.path.isdir(self.temp_path):
            os.makedirs(self.temp_path,exist_ok=True)
        self.db_connect = cyx.common.base.DbConnect()
        self.filename_only = pathlib.Path(file_path).stem
        if "consumer_" not in self.filename_only:
            raise Exception(f"Consumer file name is in valid. '{self.filename_only}' not start with 'consumer_'")
        self.msg_type = self.filename_only[len("consumer_"):].upper()
        self.msg_value = cyx.common.msg.MsgEnum.__dict__.get(self.msg_type)
        if not self.msg_value:
            file_ends = ", ".join(
                [x for x in list(cyx.common.msg.MsgEnum.__dict__.keys()) if x[0:2] != '__' and x[:-2] != '__']
            )
            raise Exception(f"{self.filename_only} file name is in valid. file name must end with [{file_ends}]")
        if not hasattr(self, "on_message"):
            raise Exception(f"{type(self).__module__}/{type(self).__name__}  in {file_path} do not have on_message")
        if not callable(self.on_message):
            raise Exception(
                f"{type(self).__module__}/{type(self).__name__}.on_message  in {file_path} must be class method")
        from cyx.common.rabitmq_message import RabitmqMsg
        self.broker = RabitmqMsg()
        self.broker.consume(self.on_message, self.msg_type)

    def get_physical_path_of_main_file_content(self, msg: cyx.common.msg.MessageInfo) -> typing.Optional[str]:
        if msg.Data.get("MainFileId"):
            local_path = msg.Data["MainFileId"]
            if isinstance(local_path, str):
                if '://' in local_path:
                    from cyx.common import config
                    rel_local_path = local_path.split("://")[1]
                    ret_file_path = os.path.join(config.file_storage_path, local_path.split("://")[1])
                    if not os.path.isfile(ret_file_path):
                        raise FileNotFoundError(f"The file '{ret_file_path}' does not exist.")
                    return ret_file_path
            return None

    def get_physical_path(self, msg: cyx.common.msg.MessageInfo) -> typing.Optional[str]:
        return msg.Data.get("ProcessFilePath")

    def set_physical_path(self, msg: cyx.common.msg.MessageInfo, file_path: str):
        if os.path.isfile(file_path):
            msg.Data["ProcessFilePath"] = file_path
        else:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    def get_output_file(self, msg: cyx.common.msg.MessageInfo, file_path: str,file_ext:str):
        id = msg.Data["_id"]
        out_dir = os.path.join(self.temp_path,msg.AppName,id)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir,exist_ok=True)
        output_file_name = os.path.split(file_path)[1]
        ret = os.path.join(out_dir,output_file_name+file_ext)
        return ret


