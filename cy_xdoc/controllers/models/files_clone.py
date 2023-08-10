import cy_web, cy_kit, cy_xdoc.auths, fastapi
from typing import Union, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ErrorType(Enum):
    NONE = 0
    FILE_NOT_FOUND = 1


@cy_web.model(all_fields_are_optional=True)
class VideoInfoClass:
    Width: int
    Height: int
    Duration: int


@cy_web.model()
class CloneFileInfo:
    UploadId: str
    FileName: str
    FileNameOnly: str
    FileExt: str
    HasThumb: bool
    SizeInBytes: int
    FullUrl: str
    RelUrl: str
    UrlThumb: str
    RelUrlThumb: str
    HasOCR: bool
    UrlOCR: str
    RelUrlOCR: str
    UrlOfServerPath: str
    RelUrlOfServerPath: str
    MimeType: str
    IsPublic: bool
    Status: int
    VideoInfo: Optional[VideoInfoClass]


@cy_web.model(all_fields_are_optional=True)
class ErrorInfo:
    Code: str
    Message: str

@cy_web.model(all_fields_are_optional=True)
class CloneFileResult:
    Info: dict
    Error: ErrorInfo


# def get_info(UploadId: str) -> dict:
#     global __copy_info__
#     global __lock__
#     if __copy_info__.get(UploadId) is None:
#         __lock__.acquire()
#         try:
#             __copy_info__[UploadId] = dict()
#         finally:
#             __lock__.release()
#     return __copy_info__[UploadId]


# def create_new_file(upload_id, info_key: str, db_context, info: dict, fs: AsyncIOMotorGridOut,
#                     update_status_when_copy_complete: bool = False) -> str:
#     db = db_context.db.delegate
#     file: gridfs.GridOut = fs.delegate
#     info[info_key] = {
#         "id": str(file._id),
#         "len": file.length,
#         "size": 0
#     }
#     chunk_size = file.chunk_size
#
#     n_fs = gridfs.GridFS(db)
#     n_f = n_fs.new_file(
#         chunk_size=chunk_size,
#         content_type=file.content_type,
#
#     )
#     ret = str(n_f._id)
#     info[info_key]["n_id"] = ret
#
#     def do_copy(s_f: gridfs.GridIn, d_f: gridfs.GridIn, chunk_size: int,update_status_when_copy_complete:bool):
#         bff = s_f.read(chunk_size)
#
#         while bff.__len__() > 0:
#             d_f.write(bff)
#             info[info_key]['size'] = info[info_key].get('size', 0) + bff.__len__()
#             bff = s_f.read(chunk_size)
#             print(info[info_key])
#
#         d_f.close()
#         if update_status_when_copy_complete:
#             db_context.update_one(
#                 Files,
#                 Files._id == upload_id,
#                 Files.Status == 1
#             )
#
#     th = threading.Thread(target=do_copy, args=(file, n_f, chunk_size,update_status_when_copy_complete,))
#     th.start()
#
#     return ret


# @cy_web.hanlder("post", "{app_name}/files/clone")
# async def clone(app_name: str, UploadId: str,
#                 token: str = fastapi.Depends(cy_xdoc.auths.Authenticate)) -> CloneFileResult:
#     """
#     Hàm sao chép 1 media sang 1
#     :param app_name:
#     :param UploadId:
#     :param token:
#     :return:
#     """
#     container = enig_frames.containers.Container
#     ret_copy = CloneFileResult()
#     # 2123d6ba-7c77-4a98-b4b7-7d45c8bc97ab
#     db_name = container.db_context.get_db_name(app_name)
#     if db_name is None:
#         return Response(status_code=403)
#
#     db_context = get_db_context(db_name)
#     item = await db_context.find_one_async(Files, Files._id == UploadId)
#     if item is None:
#         ret_copy.Error = ErrorInfo()
#         ret_copy.Error.Code = ErrorType.FILE_NOT_FOUND
#         ret_copy.Error.Message = "File not found"
#         return ret_copy
#     global __copy_info__
#     info = get_info(UploadId)
#
#     item[Files._id.__name__] = str(uuid.uuid4())
#
#     main_file_id = item.get(Files.MainFileId.__name__)
#     fsg: AsyncIOMotorGridOut = await db_context.get_file_by_id(main_file_id)
#     new_main_file_id = create_new_file(item[Files._id.__name__], Files.MainFileId.__name__, db_context, info, fsg, True)
#     item[Files.MainFileId.__name__] = new_main_file_id
#     item[Files.RegisterOn.__name__] = datetime.datetime.utcnow()
#     item[Files.ServerFileName.__name__] = f"{item[Files._id.__name__]}.{item[Files.FileExt.__name__]}"
#     item[Files.FullFileName.__name__] = f"{item['_id']}/{item[Files.FileName.__name__]}"
#     item[Files.FullFileNameLower.__name__] = f"{item['_id']}/{item[Files.FileName.__name__]}".lower()
#     item[Files.Status.__name__] = 0
#
#     try:
#         n_item = await db_context.insert_one_async(Files, item)
#         ret = CloneFileInfo()
#         ret.UploadId: str = n_item["_id"]
#         ret.FileName = n_item.get(Files.FileName.__name__)
#         ret.FileNameOnly = n_item.get(Files.FileNameOnly.__name__)
#         ret.FileExt = n_item.get(Files.FileExt.__name__)
#         ret.HasOCR = n_item.get(Files.OCRFileId.__name__) is not None
#         ret.MimeType = n_item.get(Files.MimeType.__name__)
#         ret.SizeInBytes = n_item.get(Files.SizeInBytes.__name__)
#         ret.IsPublic = n_item.get(Files.IsPublic.__name__)
#         ret.Status = n_item.get(Files.Status.__name__)
#         ret.RelUrl = f"api/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}"
#         ret.FullUrl = f"{container.Services.host.root_api_url}/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}"
#         ret.HasThumb = n_item.get(Files.HasThumb.__name__)
#
#         if ret.HasThumb:
#             thumb_file_id = item.get(Files.ThumbFileId.__name__)
#             if thumb_file_id is not None:
#                 fsg_thumb: AsyncIOMotorGridOut = await db_context.get_file_by_id(thumb_file_id)
#                 new_thumb_file_id = create_new_file(item[Files._id.__name__], Files.ThumbFileId.__name__, db_context,
#                                                     info, fsg_thumb)
#                 await db_context.update_one_async(Files, Files._id == ret.UploadId,
#                                                   Files.ThumbFileId == new_thumb_file_id)
#             """
#             http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
#             """
#             ret.RelUrlThumb = f"api/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}.png"
#             ret.UrlThumb = f"{container.Services.host.root_api_url}/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}.png"
#         if ret.HasOCR:
#             """
#             http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
#             """
#             ret.RelUrlOCR = f"api/{app_name}/file-ocr/{ret.UploadId}/{ret.FileName.lower()}.pdf"
#             ret.UrlOCR = f"{container.Services.host.root_api_url}/{app_name}/file-ocr/{ret.UploadId}/{ret.FileName.lower()}.pdf"
#             ocr_file_id = item.get(Files.OCRFileId.__name__)
#             if ocr_file_id is not None:
#                 fsg_ocr: AsyncIOMotorGridOut = await db_context.get_file_by_id(ocr_file_id)
#                 new_ocr_file_id = create_new_file(item[Files._id.__name__], Files.OCRFileId.__name__, db_context,
#                                                   info, fsg_ocr)
#                 await db_context.update_one_async(Files, Files._id == ret.UploadId,
#                                                   Files.OCRFileId == new_ocr_file_id)
#         if item.get(Files.VideoDuration.__name__) is not None:
#             ret.VideoInfo = VideoInfoClass()
#             ret.VideoInfo.Width = n_item.get(Files.VideoResolutionWidth.__name__)
#             ret.VideoInfo.Height = n_item.get(Files.VideoResolutionHeight.__name__)
#             ret.VideoInfo.Duration = n_item.get(Files.VideoDuration.__name__)
#         bool_body = {
#             "bool": {
#                 "must":
#                     {"prefix": {
#                         "path.virtual": f'/{app_name}/{UploadId}'}}
#             }
#         }
#         resp = search_engine.get_client().search(index=fasty.config.search_engine.index, query=bool_body)
#         if resp.body.get('hits') and resp.body['hits']['hits'] and resp.body['hits']['hits'].__len__() > 0:
#             es_id = resp.body['hits']['hits'][0]['_id']
#             body = resp.body['hits']['hits'][0].get('_source')
#             body['path']['virtual'] = f'/{app_name}/{ret.UploadId}.{item[Files.FileExt.__name__]}'
#             body['MarkDelete'] = False
#             search_engine.get_client().index(
#                 index=fasty.config.search_engine.index,
#                 id=ret.UploadId,
#                 body=body)
#
#         ret_copy.Info = ret
#     except Exception as e:
#         print(e)
#
#     return ret_copy
