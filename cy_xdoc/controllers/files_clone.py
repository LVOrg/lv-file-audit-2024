# import pydantic
#
# import cy_kit
# import cy_web, fastapi, cy_xdoc, cy_xdoc.auths
#
# from cy_xdoc.controllers.models.files_clone import CloneFileResult
# import cy_xdoc.services.files
# @cy_web.hanlder(method= "post", path= "{app_name}/files/clone")
# def clone_to_new(app_name:str, UploadId: str, token = fastapi.Depends(cy_xdoc.auths.Authenticate)) -> CloneFileResult:
#
#     file_service:cy_xdoc.services.files.FileServices = cy_kit.singleton(cy_xdoc.services.files.FileServices)
#
#     item = file_service.do_copy(app_name=app_name,upload_id=UploadId)
#
#     if item is None:
#         return CloneFileResult(
#             Error= pydantic.BaseModel(
#                 Code="fileNotFound",
#                 Message="File not found"
#
#             )
#         )
#     else:
#
#
#         return  CloneFileResult(
#             Info = item.to_json_convertable()
#         )
#
#
#
#
#
#
#
#
#
#
