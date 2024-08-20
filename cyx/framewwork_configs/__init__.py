# import importlib
# import cy_kit
# from cyx.loggers import LoggerService
# loggers = cy_kit.singleton(LoggerService)
#
# try:
#     from cyx.common import config
#     storage_service = None
#     if hasattr(config,"services"):
#         services_list = config.services
#         if isinstance(services_list,str):
#             services_list = services_list.split(',')
#         for x in services_list:
#             x = x.lstrip(' ').rstrip(' ')
#             if len(x)==0:
#                 continue
#             from_class = x.split("->")[0]
#             to_class =  x.split("->")[1]
#             cy_kit.config_provider(
#                 from_class =from_class,
#                 implement_class = to_class
#             )
#             #cyx.common.file_storage_mongodb.MongoDbFileService
#             from cyx.common.file_storage_mongodb import MongoDbFileService,MongoDbFileReader
#
#
# except Exception as e:
#     loggers.error(e,more_info=dict(
#         message="config storage error. Skip and use default",
#         config = getattr(config,"services")
#     ))
