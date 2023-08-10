import bson

sys_messages_document_name = "Sys_messages_v4"
import datetime
import cy_docs
@cy_docs.define(
    name=sys_messages_document_name,
    indexes=["MsgType", "CreatedOn", "AppName", "MsgId"]
)
class SysMessage:
    """
    Message
    """
    MsgId: str
    AppName: str
    MsgType: str
    Data: str
    CreatedOn: datetime.datetime
    IsFinish: bool
    IsLock: bool
    InstancesLock: dict
    RunInsLock: str
    LockedBy: dict
    UnlockCount:int

@cy_docs.define(
    name="fs.files",
    uniques=["rel_file_path"],
    indexes=["filename","uploadDate"]
)
class FsFile:
    _id: bson.ObjectId
    rel_file_path: str
    filename: str
    contentType: str
    uploadDate:datetime.datetime
    length:int

@cy_docs.define(
    name="fs.chunks",
    indexes=["files_id", "n", "files_id,n"]
)
class FsChunks:
    files_id: bson.ObjectId
    n: int
    data: bytes