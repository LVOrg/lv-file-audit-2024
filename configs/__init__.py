import pymongo

import cy_kit
import cyx.common.file_storage
from cyx.common import config
import cyx.common.msg_mongodb
import cyx.common.msg
import cyx.common.file_storage_mongodb

# cy_kit.config_provider(
#     from_class=cyx.common.file_storage.FileStorageService,
#     implement_class=cyx.common.file_storage_mongodb.MongoDbFileService
# )

"""
Cau hinh luu file dung mongodb
"""
# cy_kit.config_provider(
#     from_class=cyx.common.msg.MessageService,
#     implement_class=cyx.common.msg_mongodb.MessageServiceMongodb
# )
"""
Cau hinh he thong msg dung Mongodb
"""
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
# if isinstance(config.get('rabbitmq'), dict):
#     cy_kit.config_provider(
#         from_class=MessageService,
#         implement_class=RabitmqMsg
#     )
# else:
#     cy_kit.config_provider(
#         from_class=MessageService,
#         implement_class=Broker
#     )