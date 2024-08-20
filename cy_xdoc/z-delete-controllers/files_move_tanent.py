# import typing
# import uuid
#
# import fastapi
# import cy_xdoc.services.files
# import cy_web
# import cy_xdoc
# from cy_xdoc.auths import Authenticate
# import cyx.common.msg
#
# import cy_kit
# from cy_xdoc.services.apps import AppServices
# app_service = cy_kit.single(AppServices)

# @cy_web.hanlder("post", "admin/files/move_tenant")
# def move_tenant(Data:DataMoveTanent, token=fastapi.Depends(Authenticate)):
#     if not app_service.get_item(
#         app_name='admin',
#         app_get=Data.FromAppName
#     ):
#         return dict(
#             error=dict(
#                 message=f"{Data.FromAppName} was not found"
#             )
#         )
#     if not app_service.get_item(
#         app_name='admin',
#         app_get=Data.ToAppName
#     ):
#         return dict(
#             error=dict(
#                 message=f"{Data.ToAppName} was not found"
#             )
#         )
#     if Data.FromAppName==Data.ToAppName:
#         return dict(
#             error=dict(
#                 message=f"Can not move from '{Data.FromAppName}' to '{Data.ToAppName}'"
#             )
#         )
#     from cy_xdoc.services.files import FileServices
#     from cyx.common.file_storage_mongodb import MongoDbFileStorage
#     from cyx.common.brokers import Broker
#     from cyx.common.temp_file import TempFiles
#     file_service: FileServices = cy_kit.singleton(FileServices)
#     file_storage_service: MongoDbFileStorage = cy_kit.singleton(MongoDbFileStorage)
#
#     broker: Broker = cy_kit.singleton(Broker)
#     obsever_id = str(uuid.uuid4())
#     broker.emit(
#         app_name="admin",
#         message_type=cyx.common.msg.MSG_FILE_MOVE_TENANT,
#         data=dict(
#             from_app=Data.FromAppName,
#             to_app=Data.ToAppName,
#             ids=Data.UploadIds,
#             obsever_id=obsever_id
#         )
#     )
#     return obsever_id