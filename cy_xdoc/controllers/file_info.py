# import typing, cy_kit, cy_web, cy_xdoc.auths
# from fastapi import Depends, Response
#
# import cy_docs
# import cy_xdoc.services.files
# import cy_xdoc.models.files
#
#
# @cy_web.model()
# class VideoInfoClass:
#     Width: int
#     Height: int
#     Duration: int
#
#
# @cy_web.model(all_fields_are_optional=True)
# class UploadInfoResult:
#     UploadId: str
#     FileName: str
#     FileNameOnly: str
#     FileExt: str
#     HasThumb: bool
#     SizeInBytes: int
#     FullUrl: str
#     RelUrl: str
#     UrlThumb: str
#     RelUrlThumb: str
#     HasOCR: bool
#     UrlOCR: typing.Optional[str]
#     RelUrlOCR: typing.Optional[str]
#     UrlOfServerPath: typing.Optional[str]
#     RelUrlOfServerPath: typing.Optional[str]
#     MimeType: str
#     IsPublic: bool
#     Status: int
#     VideoInfo: typing.Optional[VideoInfoClass]
#     AvailableThumbs: typing.List[str]
#     MarkDelete:typing.Optional[bool]
#     Privileges: typing.Optional[dict]
#     ClientPrivileges:typing.Optional[typing.List[dict]]
#
#
# @cy_web.hanlder(method="post", path="{app_name}/files/info")
# def get_info(app_name: str, UploadId: str, token=Depends(cy_xdoc.auths.Authenticate)) -> UploadInfoResult:
#     """
#     APi này lay chi tiet thong tin cua Upload
#     :param app_name:
#     :return:
#     """
#     file_service:cy_xdoc.services.files.FileServices = cy_kit.single(cy_xdoc.services.files.FileServices)
#     doc_context = file_service.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
#     upload_info = doc_context.context @ UploadId
#     if upload_info is None:
#         return None
#     upload_info.UploadId = upload_info._id
#     upload_info.HasOCR = upload_info.OCRFileId is not None
#     upload_info.RelUrl = f"api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
#     upload_info.FullUrl = f"{cy_web.get_host_url()}/api/{app_name}/file/{upload_info.UploadId}/{upload_info.FileName.lower()}"
#     upload_info.HasThumb = upload_info.ThumbFileId is not None
#     available_thumbs = upload_info.AvailableThumbs or []
#     upload_info.AvailableThumbs = []
#     for x in available_thumbs:
#         upload_info.AvailableThumbs += [f"api/{app_name}/{x}"]
#     if upload_info.HasThumb:
#         """
#         http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
#         """
#         upload_info.RelUrlThumb = f"api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
#         upload_info.UrlThumb = f"{cy_web.get_host_url()}/api/{app_name}/thumb/{upload_info.UploadId}/{upload_info.FileName.lower()}.webp"
#     if upload_info.HasOCR:
#         """
#         http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
#         """
#         upload_info.RelUrlOCR = f"api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
#         upload_info.UrlOCR = f"{cy_web.get_host_url()}/api/{app_name}/file-ocr/{upload_info.UploadId}/{upload_info.FileName.lower()}.pdf"
#     if upload_info.VideoResolutionWidth:
#         upload_info.VideoInfo = cy_docs.DocumentObject()
#         upload_info.VideoInfo.Width = upload_info.VideoResolutionWidth
#         upload_info.VideoInfo.Height = upload_info.VideoResolutionHeight
#         upload_info.VideoInfo.Duration = upload_info.VideoDuration
#     if upload_info.ClientPrivileges and not isinstance(upload_info.ClientPrivileges,list):
#         upload_info.ClientPrivileges = [upload_info.ClientPrivileges]
#     if upload_info.ClientPrivileges is None:
#         upload_info.ClientPrivileges =[]
#     return upload_info.to_pydantic()
