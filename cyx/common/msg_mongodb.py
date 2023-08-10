import datetime
import uuid

import cy_docs
import cy_kit
from cyx.common.msg import MessageService, MessageInfo
from typing import List
from cyx.common.base import Base
from cyx.models import SysMessage
import pathlib
import os
import re
import cyx.common.base


@cy_kit.must_imlement(MessageService)
class MessageServiceMongodb:
    def __init__(self,
                 db_connect=cy_kit.inject(cyx.common.base.DbConnect)
                 ):
        self.db_connect: cyx.common.base.DbConnect = db_connect
        self.instance_id = str(uuid.uuid4())
        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.lock_dir = os.path.join(self.working_dir, "background_service_files", "msg_lock")
        if not os.path.isdir(self.lock_dir):
            os.makedirs(self.lock_dir, exist_ok=True)
        files = list(list(os.walk(self.lock_dir))[0][2])
        val_id = None
        UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
        for x in files:
            file_name = pathlib.Path(x).stem
            if UUID_PATTERN.match(file_name):
                val_id = file_name
                break
        if val_id is None:
            with open(os.path.join(self.lock_dir, self.instance_id), 'wb') as f:
                f.write(self.instance_id.encode('utf8'))
        else:
            self.instance_id = val_id

    def emit(self, app_name: str, message_type: str, data: dict):
        doc_context = self.db_connect.db('admin').doc(SysMessage)
        doc_context.context.insert_one(
            doc_context.fields.Data << data,
            doc_context.fields.MsgType << message_type,
            doc_context.fields.CreatedOn << datetime.datetime.utcnow(),
            doc_context.fields.MsgId << str(uuid.uuid4()),
            doc_context.fields.IsLock << False,
            doc_context.fields.AppName << app_name,
            doc_context.fields.InstancesLock << {
                self.instance_id: True
            }
        )

    def re_emit(cls, msg: MessageInfo):
        """
        somehow to implement thy source here ...
        """
        pass
    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:

        doc_context = self.db_connect.db('admin').doc(SysMessage)
        filter = doc_context.fields.MsgType == message_type
        filter_not_exist_locked = cy_docs.not_exists(doc_context.fields.LockedBy)
        filter_not_is_lock = getattr(doc_context.fields.LockedBy, self.instance_id) == False

        filter = filter & (filter_not_exist_locked | filter_not_is_lock)
        ret_list = doc_context.context.aggregate().match(
            filter=filter
        ).sort(
            doc_context.fields.CreatedOn.asc()
        ).limit(max_items)

        ret = []
        for x in ret_list:
            fx = MessageInfo()
            fx.MsgType = x.MsgType
            fx.Data = x.Data
            fx.AppName = x.AppName
            fx.CreatedOn = x.CreatedOn
            fx.Id = x.MsgId
            self.lock(fx)
            ret += [fx]
            # doc_context.context.update(
            #     doc_context.fields.MsgId == x.MsgId,
            #     doc_context.fields.IsLock <<True
            # )

        return ret

    def unlock(self, item: MessageInfo, limit_unlock_count=10):
        """
        somehow to implement thy source here ...
        """
        docs = self.db_connect.db('admin').doc(SysMessage)
        unlock_count = item.get("UnlockCount") or 0
        if unlock_count > limit_unlock_count:
            self.delete(item)
        else:
            docs.context.update(
                docs.fields.MsgId == item.Id,
                docs.fields.LockedBy << {
                    self.instance_id: False
                },
                docs.fields.UnlockCount << (unlock_count + 1)
            )

    def lock(self, item: MessageInfo):
        docs = self.db_connect.db('admin').doc(SysMessage)
        docs.context.update(
            docs.fields.MsgId == item.Id,
            docs.fields.LockedBy << {
                self.instance_id: True
            }
        )

    def is_lock(self, item: MessageInfo):
        docs = self.db_connect.db('admin').doc(SysMessage)
        item = docs.context @ (docs.fields.MsgId == item.Id)
        if not item:
            return False
        elif item.get("LockedBy") is None:
            return False
        else:
            keys = item.LockedBy.keys()
            if keys.__len__() > 0:
                return self.instance_id not in item.LockedBy.keys()
            else:
                return False

    def delete(self, item: MessageInfo):

        docs = self.db_connect.db('admin').doc(SysMessage)
        docs.context.delete(
            docs.fields.MsgId == item.Id
        )

    def reset_status(self, message_type: str):
        """
            Reset status
            :param message_type:
            :return:
                """
        docs = self.db_connect.db('admin').doc(SysMessage)
        docs.context.update(
            docs.fields.MsgType == message_type,
            docs.fields.IsLock << False,
            docs.fields.RunInsLock << None
        )

    def get_type(self) -> str:
        """
        somehow to implement thy source here ...
        """
        return "mongodb"

    def consume(self,handler,msg_type:str):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def close(self):
        """
        somehow to implement thy source here ...
        """
        pass