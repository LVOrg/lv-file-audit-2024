"""
The main class in this package is FileServices. FileServices supports fully access to DocUploadRegister Collection
"""
import datetime
import mimetypes
import os.path
import pathlib
import shutil
import threading
import time
import typing
import uuid

import bson
import humanize
import cy_docs
import cy_kit
import cy_web
import gridfs.errors
from cy_xdoc.models.files import DocUploadRegister, Privileges, PrivilegesValues
import cyx.common.file_storage
import cy_xdoc.services.search_engine
import cyx.common.base
import cyx.common.cacher
import traceback
from cyx.loggers import LoggerService
from cyx.cache_service.memcache_service import MemcacheServices

from cyx.common.file_storage_mongodb import MongoDbFileService
from cyx.common.msg import MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE
from cyx.common import config
from cy_fucking_whore_microsoft.services.ondrive_services import OnedriveService
from cy_fucking_whore_microsoft.fwcking_ms.caller import FuckingWhoreMSApiCallException
from cyx.common.rabitmq_message import RabitmqMsg


class FileServices:
    """
    The service access to FileUploadRegister MongoDb Collection
    """

    def __init__(self,
                 file_storage_service: MongoDbFileService = cy_kit.singleton(
                     MongoDbFileService),
                 search_engine=cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine),
                 db_connect=cy_kit.singleton(cyx.common.base.DbConnect),
                 cacher=cy_kit.singleton(cyx.common.cacher.CacherService),
                 logger=cy_kit.singleton(LoggerService),
                 memcache_service=cy_kit.singleton(MemcacheServices),
                 onedrive_service=cy_kit.singleton(OnedriveService),
                 broker: RabitmqMsg = cy_kit.singleton(RabitmqMsg)):
        self.onedrive_service = onedrive_service
        self.file_storage_service = file_storage_service
        self.search_engine = search_engine
        self.db_connect = db_connect
        # self.cacher = cacher
        self.cache_type = f"{DocUploadRegister.__module__}.{DocUploadRegister.__name__}"
        self.logger = logger
        self.memcache_service = memcache_service
        self.config = config
        self.broker = broker

    def get_queryable_doc(self, app_name: str) -> cyx.common.base.DbCollection[DocUploadRegister]:
        """
        MongoDb DocUploadRegister Collection as Queryable
        :param app_name: Tenant of Mongodb database
        :return:
        """
        doc = self.db_connect.db(app_name).doc(DocUploadRegister)
        return doc

    def get_list(self, app_name, root_url, page_index: int, page_size: int,
                 field_search: typing.Optional[str] = "FileName",
                 value_search: typing.Optional[str] = None,
                 doc_type: typing.Optional[str] = None):

        doc = self.db_connect.db(app_name).doc(DocUploadRegister)
        filter = None
        arrg = doc.context.aggregate()
        if value_search is not None and value_search != "":
            filter = getattr(doc.fields, field_search).like(value_search)

        if doc_type and doc_type != "AllTypes" and doc_type!="Uncategorized":
            if filter:
                filter = filter & (doc.fields.DocType == doc_type)
            else:
                filter = (doc.fields.DocType == doc_type)
        if doc_type and doc_type == "Uncategorized":
            if filter:
                filter = filter & (cy_docs.not_exists(doc.fields.DocType))
            else:
                filter = (cy_docs.not_exists(doc.fields.DocType))
        if filter:
            arrg = arrg.match(filter)
        items = None
        try:
            items = arrg.sort(
                doc.fields.RegisterOn.desc(),
                doc.fields.Status.desc()
            ).skip(page_size * page_index).limit(page_size).project(
                cy_docs.fields.UploadId >> doc.fields.id,
                doc.fields.FileName,
                doc.fields.Status,
                doc.fields.SizeInHumanReadable,
                doc.fields.ServerFileName,
                doc.fields.IsPublic,
                doc.fields.FullFileName,
                doc.fields.MimeType,
                cy_docs.fields.FileSize >> doc.fields.SizeInBytes,
                cy_docs.fields.UploadID >> doc.fields.Id,
                cy_docs.fields.CreatedOn >> doc.fields.RegisterOn,
                doc.fields.FileNameOnly,
                cy_docs.fields.UrlOfServerPath >> cy_docs.concat(root_url, f"/api/{app_name}/file/",
                                                                 doc.fields.FullFileName),
                cy_docs.fields.RelUrlOfServerPath >> cy_docs.concat(f"api/{app_name}/file/", doc.fields.FullFileName),
                cy_docs.fields.ThumbUrl >> cy_docs.concat(root_url, f"/api/{app_name}/thumb/", doc.fields.FullFileName,
                                                          ".webp"),
                doc.fields.AvailableThumbs,
                doc.fields.HasThumb,
                doc.fields.OCRFileId,
                cy_docs.fields.Media >> (
                    cy_docs.fields.Width >> doc.fields.VideoResolutionWidth,
                    cy_docs.fields.Height >> doc.fields.VideoResolutionHeight,
                    cy_docs.fields.Duration >> doc.fields.VideoDuration,
                    cy_docs.fields.FPS >> doc.fields.VideoFPS
                ),
                doc.fields.SearchEngineErrorLog,
                doc.fields.SearchEngineMetaIsUpdate,
                doc.fields.BrokerMsgUploadIsOk,
                doc.fields.BrokerErrorLog,
                doc.fields.StorageType,
                doc.fields.RemoteUrl,
                doc.fields.DocType,
                doc.fields.HasSearchContent,
                doc.fields.ThumbnailsAble,
                doc.fields.IsEncryptContent,
                doc.fields.IsLvOcrError,
                doc.fields.IsSearchEngineError,
                doc.fields.ProcessInfo

            )
            self.logger.info("Get list of files is OK")
        except Exception as e:
            self.logger.info("Get list of files is error")
            self.logger.error(e)

        from cyx.common.content_marterial_utils import check_is_thumbnails_able
        try:
            for x in items:
                _a_thumbs = []
                if x.AvailableThumbs is not None:
                    for url in x.AvailableThumbs:
                        _a_thumbs += [f"api/{app_name}/thumbs/{url}"]
                    x["AvailableThumbs"] = _a_thumbs
                if x.OCRFileId:
                    x["OcrContentUrl"] = f"{root_url}/api/{app_name}/file-ocr/{x.UploadID}/{x.FileNameOnly.lower()}.pdf"
                if check_is_thumbnails_able(x):
                    x["HasThumb"] = True
                yield x
        except Exception as e:
            self.logger.error(e)

    def get_main_file_of_upload(self, app_name, upload_id):
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
        if not upload:
            return
        if upload.MainFileId is None:
            return None
        fs = self.file_storage_service.get_file_by_id(
            app_name=app_name,
            id=str(upload.MainFileId)
        )
        # self.get_file(app_name, upload.MainFileId)
        return fs

    async def get_main_file_of_upload_async(self, app_name, upload_id):
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
        if not upload:
            return

        if upload.MainFileId is not None:
            fs = await self.get_file_async(app_name, upload.MainFileId)
            return fs
        else:
            return None

    def find_file_async(self, app_name, relative_file_path):
        pass

    def get_main_main_thumb_file(self, app_name: str, upload_id: str):
        try:
            upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
            if upload is None:
                return None
            ret = self.file_storage_service.get_file_by_id(app_name=app_name, id=upload.ThumbFileId)
            # self.get_file(app_name, upload.ThumbFileId)
            return ret
        except gridfs.errors.NoFile as e:
            return None

    async def get_main_main_thumb_file_async(self, app_name: str, upload_id: str):
        doc_context = self.db_connect.db(app_name).doc(DocUploadRegister)
        upload = await doc_context.context.find_one_async(
            doc_context.fields.id == upload_id
        )

        if upload is None:
            return None
        try:
            path_str = pathlib.Path(upload.MainFileId).parent.__str__()
            path_str = path_str.replace("local:/", "local://") + "/700.webp"
            if upload.ThumbFileId is None:

                upload.ThumbFileId = path_str

            rela_file_path= os.path.join(config.file_storage_path,path_str.split("://")[1])
            ret = await self.file_storage_service.get_file_by_id_async(app_name=app_name, id=upload.ThumbFileId)
            # self.get_file(app_name, upload.ThumbFileId)
            return ret
        except gridfs.errors.NoFile as e:
            file_name_lower = upload[doc_context.fields.FileNameLower]
            if '/' in file_name_lower:
                _dir_, _file_ = os.path.split(upload[doc_context.fields.FileNameLower])
                directory = _dir_ + ".webp"
            else:
                directory = file_name_lower + ".webp"
            register_date: datetime.datetime = upload[doc_context.fields.RegisterOn]
            file_ext = upload[doc_context.fields.FileExt]
            if file_ext is None:
                file_ext = "unknown"
            else:
                file_ext = file_ext[0:3]

            directory = f"{app_name}/{register_date.year}/{register_date.month:02d}/{register_date.day:02d}/{file_ext}/{upload_id}/{directory}"
            await doc_context.context.update_async(
                doc_context.fields.id == upload_id,
                doc_context.fields.ThumbFileId << f"local://{directory}"
            )
            ret = await self.file_storage_service.get_file_by_id_async(app_name=app_name, id=directory)
            # self.get_file(app_name, upload.ThumbFileId)
            return ret

    async def add_new_upload_info_async(self,
                                        app_name: str,
                                        client_file_name: str,
                                        is_public: bool,
                                        file_size: int,
                                        chunk_size: int,
                                        thumbs_support: str,
                                        web_host_root_url: str,
                                        privileges_type,
                                        storage_type: str,
                                        onedriveScope: str,
                                        meta_data: typing.Optional[dict] = None,
                                        skip_option: typing.Optional[dict] = None,
                                        onedrive_password: typing.Optional[str] = None,
                                        onedrive_expiration: typing.Optional[str] = None,
                                        is_encrypt_content: typing.Optional[bool] = False
                                        ):
        return self.add_new_upload_info(
            app_name=app_name,
            client_file_name=client_file_name,
            is_public=is_public,
            file_size=file_size,
            chunk_size=chunk_size,
            thumbs_support=thumbs_support,
            web_host_root_url=web_host_root_url,
            privileges_type=privileges_type,
            meta_data=meta_data,
            skip_option=skip_option,
            storage_type=storage_type,
            onedriveScope=onedriveScope,
            onedrive_password=onedrive_password,
            onedrive_expiration=onedrive_expiration,
            is_encrypt_content = is_encrypt_content

        )

    def add_new_upload_info(self,
                            app_name: str,
                            client_file_name: str,
                            is_public: bool,
                            file_size: int,
                            chunk_size: int,
                            thumbs_support: str,
                            web_host_root_url: str,
                            privileges_type,
                            storage_type: str,
                            onedriveScope: str,
                            meta_data: typing.Optional[dict] = None,
                            skip_option: typing.Optional[dict] = None,
                            onedrive_password: typing.Optional[str] = None,
                            onedrive_expiration: typing.Optional[str] = None,
                            is_encrypt_content: typing.Optional[bool] = False):
        __registerde_on__ = datetime.datetime.utcnow()
        id = str(uuid.uuid4())
        _has_thumb_ = False
        file_ext = pathlib.Path(client_file_name).suffix
        local_path_dir: str = self.make_local_path(
            register_on=__registerde_on__,
            file_ext=file_ext,
            app_name=app_name,
            upload_id=id
        )
        thumbs_size = [int(x) for x in (thumbs_support or "").split(",") if x.isnumeric()]
        mt, _ = mimetypes.guess_type(client_file_name
                                     )
        if "video/" in mt or 'image/' in mt:
            _has_thumb_ = True

        server_file_name_only = ""
        for x in client_file_name:
            if x in "!@#$%^&*()+<>?[]:'\"~=+":
                server_file_name_only += "_"
            else:
                server_file_name_only += x
        doc = self.db_connect.db(app_name).doc(DocUploadRegister)

        mime_type, _ = mimetypes.guess_type(client_file_name)
        num_of_chunks, tail = divmod(file_size, chunk_size)
        if tail > 0:
            num_of_chunks += 1
        privileges_server, privileges_client = self.create_privileges(
            app_name=app_name,
            privileges_type_from_client=privileges_type
        )
        fucking_session_url = None
        fucking_onedrive_item = None
        if storage_type == "onedrive":
            fucking_session_url = self.onedrive_service.get_upload_session(
                app_name=app_name,
                upload_id=id,
                client_file_name=client_file_name
            )
            fucking_onedrive_item = self.onedrive_service.get_access_item(
                app_name=app_name,
                upload_id=id,
                client_file_name=client_file_name
            )

        def cahe_register():
            cache_doc = cy_docs.DocumentObject()
            cache_doc[doc.fields.id] = id
            cache_doc[doc.fields.FileName] = client_file_name
            cache_doc[doc.fields.FileNameOnly] = pathlib.Path(client_file_name).stem
            cache_doc[doc.fields.IsEncryptContent] = is_encrypt_content

            cache_doc[doc.fields.FileNameLower] = client_file_name.lower()
            if len(os.path.splitext(client_file_name)[1].split('.')) > 1:
                cache_doc[doc.fields.FileExt] = os.path.splitext(client_file_name)[1].split('.')[1]

            cache_doc[doc.fields.FullFileName] = f"{id}/{server_file_name_only}"
            cache_doc[doc.fields.FullFileNameLower] = f"{id}/{server_file_name_only}".lower()
            cache_doc[doc.fields.FullFileNameWithoutExtenstion] = f"{id}/{pathlib.Path(server_file_name_only).stem}"
            cache_doc[
                doc.fields.FullFileNameWithoutExtenstionLower] = f"{id}/{pathlib.Path(server_file_name_only).stem}".lower()
            if len(os.path.splitext(server_file_name_only)[1].split('.')) > 1:
                cache_doc[
                    doc.fields.ServerFileName] = f"{id}.{os.path.splitext(server_file_name_only)[1].split('.')[1]}"
            else:
                cache_doc[
                    doc.fields.ServerFileName] = f"{id}"
            cache_doc[doc.fields.AvailableThumbSize] = thumbs_support
            cache_doc[doc.fields.ChunkSizeInKB] = chunk_size / 1024
            cache_doc[doc.fields.ChunkSizeInBytes] = chunk_size
            cache_doc[doc.fields.NumOfChunks] = num_of_chunks
            cache_doc[doc.fields.NumOfChunksCompleted] = 0
            cache_doc[doc.fields.SizeInHumanReadable] = humanize.filesize.naturalsize(file_size)
            cache_doc[doc.fields.SizeUploaded] = 0
            cache_doc[doc.fields.ProcessHistories] = []
            cache_doc[doc.fields.MimeType] = mime_type
            cache_doc[doc.fields.IsPublic] = is_public
            cache_doc[doc.fields.Status] = 0
            cache_doc[doc.fields.RegisterOn] = datetime.datetime.utcnow()
            cache_doc[doc.fields.RegisterOnDays] = datetime.datetime.utcnow().day
            cache_doc[doc.fields.RegisterOnMonths] = datetime.datetime.utcnow().month
            cache_doc[doc.fields.RegisterOnYears] = datetime.datetime.utcnow().year
            cache_doc[doc.fields.RegisterOnHours] = datetime.datetime.utcnow().hour
            cache_doc[doc.fields.RegisterOnMinutes] = datetime.datetime.utcnow().minute
            cache_doc[doc.fields.RegisterOnSeconds] = datetime.datetime.utcnow().second
            cache_doc[doc.fields.RegisteredBy] = app_name
            cache_doc[doc.fields.HasThumb] = _has_thumb_
            cache_doc[doc.fields.LastModifiedOn] = datetime.datetime.utcnow()
            cache_doc[doc.fields.SizeInBytes] = file_size
            cache_doc[doc.fields.Privileges] = privileges_server
            cache_doc[doc.fields.ClientPrivileges] = privileges_client
            cache_doc[doc.fields.meta_data] = meta_data
            cache_doc[doc.fields.SkipActions] = skip_option
            cache_doc[doc.fields.StorageType] = storage_type
            cache_doc[doc.fields.OnedriveScope] = onedriveScope
            cache_doc[doc.fields.OnedrivePassword] = onedrive_password
            cache_doc[doc.fields.OnedriveExpiration] = onedrive_expiration
            cache_doc[doc.fields.OnedriveSessionUrl] = fucking_session_url

            self.set_upload_register_to_cache(
                app_name=app_name,
                upload_id=id,
                data=cache_doc
            )

        cahe_register()

        def insert_register():
            server_file_name = id
            file_ext = None
            if len(os.path.splitext(server_file_name_only)[1].split('.')) > 1:
                file_ext = os.path.splitext(client_file_name)[1].split('.')[1]
                server_file_name = f"{id}.{file_ext}"
            retry_count = 0

            while retry_count < 10:
                try:
                    require_msg_process = cyx.common.msg.MSG_MATRIX.get(
                        (file_ext or "").lower()
                    )
                    main_thumb_file = f"{local_path_dir}/{client_file_name}.webp"

                    doc.context.insert_one(
                        doc.fields.id << id,
                        doc.fields.FileName << client_file_name,
                        doc.fields.FileNameOnly << pathlib.Path(client_file_name).stem,
                        doc.fields.FileNameLower << client_file_name.lower(),
                        doc.fields.FileExt << file_ext,
                        doc.fields.FullFileName << f"{id}/{server_file_name_only}",
                        doc.fields.FullFileNameLower << f"{id}/{server_file_name_only}".lower(),
                        doc.fields.FullFileNameWithoutExtenstion << f"{id}/{pathlib.Path(server_file_name_only).stem}",
                        doc.fields.FullFileNameWithoutExtenstionLower << f"{id}/{pathlib.Path(server_file_name_only).stem}".lower(),
                        doc.fields.ServerFileName << server_file_name,
                        doc.fields.AvailableThumbSize << thumbs_support,
                        doc.fields.ChunkSizeInKB << chunk_size / 1024,
                        doc.fields.ChunkSizeInBytes << chunk_size,
                        doc.fields.NumOfChunks << num_of_chunks,
                        doc.fields.NumOfChunksCompleted << 0,
                        doc.fields.SizeInHumanReadable << humanize.filesize.naturalsize(file_size),
                        doc.fields.SizeUploaded << 0,
                        doc.fields.ProcessHistories << [],
                        doc.fields.MimeType << mime_type,
                        doc.fields.IsPublic << is_public,
                        doc.fields.Status << 0,
                        doc.fields.RegisterOn << datetime.datetime.utcnow(),
                        doc.fields.RegisterOnDays << datetime.datetime.utcnow().day,
                        doc.fields.RegisterOnMonths << datetime.datetime.utcnow().month,
                        doc.fields.RegisterOnYears << datetime.datetime.utcnow().year,
                        doc.fields.RegisterOnHours << datetime.datetime.utcnow().hour,
                        doc.fields.RegisterOnMinutes << datetime.datetime.utcnow().minute,
                        doc.fields.RegisterOnSeconds << datetime.datetime.utcnow().second,
                        doc.fields.RegisteredBy << app_name,
                        doc.fields.HasThumb << _has_thumb_,
                        doc.fields.LastModifiedOn << datetime.datetime.utcnow(),
                        doc.fields.SizeInBytes << file_size,
                        doc.fields.Privileges << privileges_server,
                        doc.fields.ClientPrivileges << privileges_client,
                        doc.fields.meta_data << meta_data,
                        doc.fields.SkipActions << skip_option,
                        doc.fields.StorageType << storage_type,
                        doc.fields.OnedriveScope << onedriveScope,
                        doc.fields.OnedriveSessionUrl << fucking_session_url,
                        doc.fields.OnedrivePassword << onedrive_password,
                        doc.fields.OnedriveExpiration << onedrive_expiration,
                        doc.fields.MsgRequires << require_msg_process,
                        doc.fields.MainFileId << f"{local_path_dir}/{client_file_name}",
                        doc.fields.ThumbFileId << main_thumb_file,
                        doc.fields.IsEncryptContent << is_encrypt_content
                    )
                except Exception as e:
                    time.sleep(0.1)
                    retry_count += 1
                    if retry_count > 10:
                        self.logger.error(e)

        insert_register()

        def search_engine_create_or_update_privileges():
            re_try_count = 0
            while re_try_count < 3:
                try:
                    self.search_engine.create_or_update_privileges(
                        app_name=app_name,
                        upload_id=id,
                        data_item=doc.context @ id,
                        privileges=privileges_server,
                        meta_info=meta_data

                    )
                    doc.context.update(
                        doc.fields.id == id,
                        doc.fields.SearchEngineMetaIsUpdate << True
                    )
                    re_try_count = 3

                except Exception as e:
                    if re_try_count + 1 >= 3:
                        traceback_string = traceback.format_exc()
                        doc.context.update(
                            doc.fields.id == id,
                            doc.fields.SearchEngineErrorLog << traceback_string
                        )
                        self.logger.error(e)
                    str_date = datetime.datetime.now().strftime("%Y-%d-%m:%H:%M:%S")
                    print(f"{str_date}: Insert data to Elastic Search Error {e}, ret-try {re_try_count + 1}")
                    re_try_count += 1
                    time.sleep(0.5)

        if (skip_option is None or
                (isinstance(skip_option, dict) and (
                        skip_option.get(MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE, False) == False and
                        skip_option.get("All", False) == False)
                )):
            th = threading.Thread(
                target=search_engine_create_or_update_privileges,
                args=()
            )
            st = datetime.datetime.utcnow()
            th.start()
        else:
            st = datetime.datetime.utcnow()

        return cy_docs.DocumentObject(
            NumOfChunks=num_of_chunks,
            ChunkSizeInBytes=chunk_size,
            UploadId=id,
            ServerFilePath=f"{id}{os.path.splitext(server_file_name_only)[1]}",
            MimeType=mime_type,
            RelUrlOfServerPath=f"api/{app_name}/file/{id}/{pathlib.Path(server_file_name_only).name.lower()}",
            SizeInHumanReadable=humanize.filesize.naturalsize(file_size),
            UrlOfServerPath=f"{web_host_root_url}/api/{app_name}/file/{id}/{pathlib.Path(server_file_name_only).name.lower()}",
            RelUrlThumb=f"api/{app_name}/thumb/{id}/{pathlib.Path(server_file_name_only).name.lower()}.webp",
            FileSize=file_size,
            UrlThumb=f"{web_host_root_url}/api/{app_name}/thumb/{id}/{pathlib.Path(server_file_name_only).name.lower()}.webp",
            OriginalFileName=client_file_name,
            SearchEngineInsertTimeInSecond=(datetime.datetime.utcnow() - st).total_seconds()
        )

    def get_upload_register(self, app_name: str, upload_id: str) -> typing.Union[
        DocUploadRegister, cy_docs.DocumentObject]:
        return self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id

    def get_find_upload_register_by_link_file_id(self, app_name: str, file_id: str):
        context = self.db_connect.db(app_name).doc(DocUploadRegister).context
        fields = self.db_connect.db(app_name).doc(DocUploadRegister).fields
        id = bson.ObjectId(file_id)
        ret = context.find_one(
            (fields.MainFileId == id) | (fields.ThumbFileId == id) | (fields.OCRFileId == id)
        )

        return ret

    async def get_upload_register_async(self, app_name: str, upload_id: str):
        return self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id

    def get_upload_register_with_cache(self, app_name, upload_id):
        key = f"{self.cache_type}/{app_name}/{upload_id}"
        ret = self.memcache_service.get_object(key, cy_docs.DocumentObject)
        if not ret:
            ret = self.get_upload_register(app_name, upload_id)
            self.memcache_service.set_object(key, ret)
        return ret

    def set_upload_register_to_cache(self, app_name, upload_id, data):
        key = f"{self.cache_type}/{app_name}/{upload_id}"
        self.memcache_service.set_object(key, data)

    def remove_upload(self, app_name, upload_id):
        """
        Remove Upload File. The method also delete all Thumbnail Files, Main File, OCR File and main thumbnail file
        finally remove Elasticsearch document \n
        Xóa tệp tải lên. Phương pháp này cũng xóa tất cả các Tệp hình thu nhỏ, Tệp chính, Tệp OCR và tệp hình thu nhỏ chính
        cuối cùng xóa tài liệu Elaticsearch

        :param app_name:
        :param upload_id:
        :return:
        """
        collection = self.db_connect.db(app_name).doc(DocUploadRegister)
        upload = collection.context @ upload_id

        if upload is None:
            return
        if upload[collection.fields.StorageType] == "onedrive":
            try:
                self.onedrive_service.delete_upload(
                    app_name=app_name,
                    upload_id=upload_id
                )
            except FuckingWhoreMSApiCallException as e:
                if e.status == 404:
                    pass
        delete_file_list = upload.AvailableThumbs or []
        delete_file_list_by_id = []
        if upload.MainFileId is not None: delete_file_list_by_id = [str(upload.MainFileId)]
        if upload.OCRFileId is not None: delete_file_list_by_id += [str(upload.OCRFileId)]
        if upload.ThumbFileId is not None: delete_file_list_by_id += [str(upload.ThumbFileId)]

        self.file_storage_service.delete_files(app_name=app_name, files=delete_file_list, run_in_thread=True)
        self.file_storage_service.delete_files_by_id(app_name=app_name, ids=delete_file_list_by_id, run_in_thread=True)
        self.search_engine.delete_doc(app_name, upload_id)
        doc = self.db_connect.db(app_name).doc(DocUploadRegister)
        ret = doc.context.delete(cy_docs.fields._id == upload_id)

        return ret.deleted_count

    def do_copy(self, app_name, upload_id, request):

        document_context = self.db_connect.db(app_name).doc(DocUploadRegister)
        item = document_context.context @ upload_id
        main_file_id = item.MainFileId
        if item is None:
            return None
        rel_file_location = item[document_context.fields.FullFileName]
        item.id = str(uuid.uuid4())
        item[document_context.fields.FullFileName] = f"{item.id}/{item[document_context.fields.FileName]}"
        item[document_context.fields.FullFileNameLower] = item[document_context.fields.FullFileName].lower()
        item[document_context.fields.Status] = 0
        item[document_context.fields.PercentageOfUploaded] = 100
        item[document_context.fields.MarkDelete] = False
        item.ServerFileName = f"{item.id}.{item[document_context.fields.FileExt]}"
        item.RegisterOn = datetime.datetime.utcnow()
        item[document_context.fields.RegisteredBy] = "root"

        file_id_to_copy = item[document_context.fields.MainFileId]
        del item[document_context.fields.MainFileId]
        to_location = item[document_context.fields.FullFileNameLower].lower()
        new_fsg = self.file_storage_service.copy_by_id(
            app_name=app_name,
            file_id_to_copy=file_id_to_copy,
            rel_file_path_to=to_location,
            run_in_thread=True
        )
        if new_fsg.get_id().startswith("local://"):
            item[document_context.fields.MainFileId] = new_fsg.get_id()
        else:
            item[document_context.fields.MainFileId] = bson.ObjectId(new_fsg.get_id())
            if item.HasThumb:
                thumb_file_id = item.ThumbFileId
                if thumb_file_id is not None:
                    thumb_fsg = self.file_storage_service.copy_by_id(
                        app_name=app_name,
                        rel_file_path_to=f"/thumb/{item.id}/{item[document_context.fields.FileName]}.webp".lower(),
                        file_id_to_copy=thumb_file_id,
                        run_in_thread=True
                    )
                    item.ThumbFileId = bson.ObjectId(thumb_fsg.get_id())
                    item.RelUrlThumb = f"api/{app_name}/thumb/{item.UploadId}/{item.FileName.lower()}.webp"
                    item.UrlThumb = f"{cy_web.get_host_url(request)}/{item.RelUrlThumb}"
            if item.HasOCR:
                ocr_file_id = item.OCRFileId
                if ocr_file_id:
                    item.RelUrlOCR = f"api/{app_name}/file-ocr/{item.UploadId}/{item.FileName.lower()}.pdf"
                    item.UrlOCR = f"{cy_web.get_host_url(request)}/api/{item.RelUrlOCR}"
                    rel_path_to_ocr = f"file-ocr/{item.UploadId}/{item.FileName.lower()}.pdf"
                    ocr_fsg = self.file_storage_service.copy_by_id(
                        app_name=app_name,
                        file_id_to_copy=ocr_file_id,
                        rel_file_path_to=rel_path_to_ocr,
                        run_in_thread=True

                    )
                    item.OCRFileId = bson.ObjectId(ocr_fsg.get_id())
        item.RelUrl = f"api/{app_name}/{item.id}/{item.FileName.lower()}"
        item.FullUrl = f"{cy_web.get_host_url(request)}/api/{app_name}/{item.UploadId}/{item.FileName.lower()}"

        @cy_kit.thread_makeup()
        def copy_thumbs(app_name: str, to_id: str, thumbs_list: typing.List[str]):
            for x in thumbs_list:
                rel_path = x[item.id.__len__():]
                self.file_storage_service.copy(
                    app_name=app_name,
                    rel_file_path_to=f"{to_id}/{rel_path}",
                    run_in_thread=False,
                    rel_file_path_from=x
                )

        self.search_engine.copy(
            app_name, from_id=upload_id, to_id=item.id, attach_data=item, run_in_thread=True)
        item.Status = 1

        item.ThumbHeight = 700
        data_insert = document_context.fields.reduce(item, skip_require=False)
        ext_path = "unknown"
        if data_insert.get("FileExt"):
            ext_path = data_insert.FileExt[0:3]
        relocate_path = f"local://{app_name}/{data_insert.RegisterOn.year}/{data_insert.RegisterOn.month:02}/{data_insert.RegisterOn.day:02}/{ext_path}/{item.id}"
        file_name_only = pathlib.Path(item.MainFileId).stem
        file_ext_with_dot = pathlib.Path(item.MainFileId).suffix
        if file_ext_with_dot != "":
            data_insert.MainFileId = f"{relocate_path}/{file_name_only}{file_ext_with_dot}"
        else:
            data_insert.MainFileId = f"{relocate_path}/{file_name_only}"

        if not new_fsg.get_id().startswith("local://"):
            item.ThumbId = None
            copy_thumbs(app_name=app_name, to_id=data_insert._id, thumbs_list=item.AvailableThumbs or []).start()
        else:
            if isinstance(item.OCRFileId, str):
                data_insert.OCRFileId = item.OCRFileId.replace(f"/{upload_id}/", f"/{item.id}/")
            if isinstance(item.ThumbFileId, str):
                data_insert.ThumbFileId = f"{relocate_path}/{os.path.split(item.ThumbFileId)[1]}"
            if isinstance(item.AvailableThumbs, list):
                data_insert.AvailableThumbs = [
                    x.replace(f"/{upload_id}/", f"/{item.id}/") for x in item.AvailableThumbs
                ]

        ret = document_context.context.insert_one(data_insert)
        return data_insert

    def update_privileges(self, app_name: str, upload_id: str, privileges: typing.List[cy_docs.DocumentObject]):
        """
        Update clear all set new
        :param app_name:
        :param upload_id:
        :param privileges:
        :return:
        """

        server_privileges, client_privileges = self.create_privileges(
            app_name=app_name,
            privileges_type_from_client=privileges
        )

        doc_context = self.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        upload = (doc_context.context @ upload_id)
        if upload is not None:

            doc_context.context.update(
                doc_context.fields.id == upload_id,
                doc_context.fields.Privileges << server_privileges,
                doc_context.fields.ClientPrivileges << client_privileges
            )
            self.search_engine.create_or_update_privileges(
                privileges=server_privileges,
                upload_id=upload_id,
                data_item=upload.to_json_convertable(),
                app_name=app_name,
                force_replace=True
            )
        else:
            self.search_engine.create_or_update_privileges(
                privileges=server_privileges,
                upload_id=upload_id,
                data_item=None,
                app_name=app_name,
                force_replace=True
            )

    def add_privileges(self, app_name, upload_id, privileges):
        """
        Add new if not exist
        :param app_name:
        :param upload_id:
        :param privileges:
        :return:
        """
        server_privileges, client_privileges = self.create_privileges(
            app_name=app_name,
            privileges_type_from_client=privileges
        )

        doc_context = self.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        upload = (doc_context.context @ upload_id)
        old_server_privileges = upload[doc_context.fields.Privileges] or {}
        old_client_privileges = upload[doc_context.fields.ClientPrivileges] or {}
        for k, v in old_server_privileges.items():

            if server_privileges.get(k):
                server_privileges[k] = list(set(server_privileges[k] + v))

            else:
                server_privileges[k] = v

        client_privileges = []
        for k, v in server_privileges.items():
            client_privileges += [{
                k: ",".join(v)
            }]

        doc_context.context.update(
            doc_context.fields.id == upload_id,
            doc_context.fields.Privileges << server_privileges,
            doc_context.fields.ClientPrivileges << client_privileges
        )
        self.search_engine.create_or_update_privileges(
            privileges=server_privileges,
            upload_id=upload_id,
            data_item=None,
            app_name=app_name,
            force_replace=False
        )

    async def add_privileges_async(self, app_name, upload_id, privileges):
        """
        Add new if not exist
        :param app_name:
        :param upload_id:
        :param privileges:
        :return:
        """
        server_privileges, client_privileges = self.create_privileges(
            app_name=app_name,
            privileges_type_from_client=privileges
        )

        doc_context = self.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)
        upload = await doc_context.context.find_one_async(
            doc_context.fields.id == upload_id
        )
        old_server_privileges = upload[doc_context.fields.Privileges] or {}
        old_client_privileges = upload[doc_context.fields.ClientPrivileges] or {}
        for k, v in old_server_privileges.items():

            if server_privileges.get(k):
                server_privileges[k] = list(set(server_privileges[k] + v))

            else:
                server_privileges[k] = v

        client_privileges = []
        for k, v in server_privileges.items():
            client_privileges += [{
                k: ",".join(v)
            }]

        await doc_context.context.update_async(
            doc_context.fields.id == upload_id,
            doc_context.fields.Privileges << server_privileges,
            doc_context.fields.ClientPrivileges << client_privileges
        )
        self.search_engine.create_or_update_privileges(
            privileges=server_privileges,
            upload_id=upload_id,
            data_item=None,
            app_name=app_name
        )

    async def remove_privileges_async(self, app_name, upload_id, privileges):
        """
                Re
                :param app_name:
                :param upload_id:
                :param privileges:
                :return:
                """
        upload = await self.get_upload_register_async(
            app_name=app_name,
            upload_id=upload_id
        )
        if upload is None:
            return
        doc_context = self.db_connect.db(app_name).doc(cy_xdoc.models.files.DocUploadRegister)

        server_privileges, client_privileges = self.create_privileges(
            app_name=app_name,
            privileges_type_from_client=privileges
        )

        db_privileges = upload.Privileges or {}
        server_privileges_update = {}
        client_privileges_update = []
        for x in server_privileges.keys():

            values = list(set(db_privileges.get(x, [])).difference(server_privileges.get(x, [])))
            if len(values) > 0:
                server_privileges_update[x] = values
            if db_privileges.get(x):
                db_privileges.__delitem__(x)

        server_privileges_update = {**db_privileges, **server_privileges_update}
        for k, v in server_privileges_update.items():
            client_privileges_update += [{
                k: ",".join(v)
            }]
        await doc_context.context.update_async(
            doc_context.fields.id == upload_id,
            doc_context.fields.Privileges << server_privileges_update,
            doc_context.fields.ClientPrivileges << client_privileges_update
        )
        self.search_engine.create_or_update_privileges(
            privileges=server_privileges_update,
            upload_id=upload_id,
            app_name=app_name,
            data_item=None,
            force_replace=False
        )

    def create_privileges(self, app_name, privileges_type_from_client):
        """
        Chuyen doi danh sach cac dac quyen do nguoi dung tao sang dang luu tru trong mongodb va elastic search
        Dong thoi ham nay cung update lai danh sach tham khao danh cho giao dien
        Trong Mongodb la 2 ban Privileges, PrivilegesValues
        :param app_name:
        :param privileges_type_from_client:
        :return: (privileges_server,privileges_client)
        """

        privileges_server = {}
        privileges_client = []
        if privileges_type_from_client:
            privilege_context = self.db_connect.db(app_name).doc(Privileges)
            privilege_value_context = self.db_connect.db(app_name).doc(PrivilegesValues)
            check_types = dict()
            for x in privileges_type_from_client:
                if check_types.get(x.Type.lower().strip()) is None:
                    privilege_item = privilege_context.context @ (
                            privilege_context.fields.Name == x.Type.lower().strip())
                    """
                    Bo sung thong tin vao danh sach cac dac quyen va cac gia tri de tham khao
    
                    """
                    if privilege_item is None:
                        def run_insert():
                            privilege_context.context.insert_one(
                                privilege_context.fields.Name << x.Type.lower().lower().strip()
                            )

                        threading.Thread(target=run_insert).start()
                        """
                        Bo sung danh sach dac quyen, ho tro cho gia dien khi loc theo dac quyen
                        """
                    for v in x.Values.lower().split(','):
                        """
                        Bo sung danh sach dac quyen va gia tri
                        """

                        def running():
                            privileges_value_item = privilege_value_context.context @ (
                                    (
                                            privilege_value_context.fields.Value == v
                                    ) & (
                                            privilege_value_context.fields.Name == x.Type.lower().lower().strip()
                                    )
                            )
                            if not privileges_value_item:
                                """
                                Neu chua co
                                """
                                try:
                                    privilege_value_context.context.insert_one(
                                        privilege_value_context.fields.Value << v,
                                        privilege_value_context.fields.Name << x.Type.lower().lower().strip()
                                    )
                                except:
                                    pass

                        threading.Thread(target=running).start()
                    privileges_server[x.Type.lower()] = [v.strip() for v in x.Values.lower().split(',')]
                    privileges_client += [{
                        x.Type: x.Values
                    }]
                check_types[x.Type.lower().strip()] = x
        return privileges_server, privileges_client

    def get_main_file_of_upload_by_rel_file_path(self, app_name, rel_file_path, runtime_file_reader=None):
        if runtime_file_reader is not None:
            return runtime_file_reader.get_file_by_name(
                app_name=app_name,
                rel_file_path=rel_file_path
            )
        return self.file_storage_service.get_file_by_name(
            app_name=app_name,
            rel_file_path=rel_file_path
        )

    def update_main_thumb_id(self, app_name, upload_id, main_thumb_id):
        if isinstance(main_thumb_id, str) and not main_thumb_id.startswith("local://"):
            main_thumb_id = bson.ObjectId(main_thumb_id.encode())
        doc_context = self.db_connect.db(app_name).doc(DocUploadRegister)
        doc_context.context.update(
            doc_context.fields.id == upload_id,
            doc_context.fields.ThumbFileId << main_thumb_id,
            doc_context.fields.HasThumb << True
        )

    def update_available_thumbs(self, upload_id: str, app_name: str, available_thumbs: typing.List[str],
                                thumb_file_path=None):
        doc_context = self.db_connect.db(app_name).doc(DocUploadRegister)
        if thumb_file_path is not None:
            doc_context.context.update(
                doc_context.fields.id == upload_id,
                doc_context.fields.AvailableThumbs << available_thumbs,
                doc_context.fields.HasThumb << True,
                doc_context.fields.ThumbFileId << thumb_file_path
            )
        else:
            doc_context.context.update(
                doc_context.fields.id == upload_id,
                doc_context.fields.AvailableThumbs << available_thumbs,
                doc_context.fields.HasThumb << True
            )

    def update_ocr_info(self, app_name: str, upload_id: str, ocr_file_id: typing.Union[str, bson.ObjectId]):
        if isinstance(ocr_file_id, str):
            try:
                ocr_file_id = bson.ObjectId(ocr_file_id)
            except:
                upload_info = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
                if upload_info is None:
                    raise Exception(f"Upload with ID {upload_id}  was not found or deleted")
                register_on = upload_info.RegisterOn
                file_ext = upload_info.FileExt

                if isinstance(register_on, datetime.datetime) \
                        and isinstance(file_ext, str) \
                        and hasattr(self.config, "file_storage_path") and \
                        isinstance(self.config.file_storage_path, str):
                    file_ext = file_ext[0:3]
                    dir_path = os.path.join(
                        app_name, f"{register_on.year}",
                        f"{register_on.month:02}",
                        f"{register_on.day:02}",
                        file_ext,
                        upload_id,
                        "ocr"

                    )
                    full_dir_path = os.path.join(self.config.file_storage_path, dir_path)

                    if not os.path.isdir(full_dir_path):
                        os.makedirs(full_dir_path, exist_ok=True)
                        shutil.move(ocr_file_id, full_dir_path)
                        ocr_file_id = "local://" + os.path.join(dir_path, pathlib.Path(ocr_file_id).stem) + ".pdf"

        doc_context = self.db_connect.db(app_name).doc(DocUploadRegister)
        doc_context.context.update(
            doc_context.fields.id == upload_id,
            doc_context.fields.OCRFileId << ocr_file_id

        )

    def cache_upload_register_set(self,
                                  UploadId: str,
                                  doc_data: cy_docs.DocumentObject):
        pass

    def cache_upload_register_get(self, upload_id: str) -> typing.Optional[cy_docs.DocumentObject]:
        ret = self.memcache_service.get_dict(key=upload_id)
        if ret is None:
            return None
        ret_doc = cy_docs.DocumentObject(ret)
        return ret_doc

    def update_msg_check_list(self, app_name, upload_id, key: str, value):
        chk_key = f"check_list_{app_name}/{key}"

        def run():
            doc = self.db_connect.db(app_name).doc(DocUploadRegister)
            doc.context.update(
                doc.fields.id == upload_id,
                getattr(doc.fields.MsgCheckList, key.replace(".", "_")) << value
            )

        chk = self.memcache_service.get_dict(chk_key) or {}
        if chk is None:
            chk[key.replace(".", "_")] = value
            threading.Thread(target=run).start()

    def get_msg_check_list(self, app_name, upload_id, key: str) -> typing.Optional[int]:
        if upload_id is None:
            return -1
        chk_key = f"check_list_{app_name}/{key}"
        chk_cache = self.memcache_service.get_dict(chk_key)
        if chk_cache is None:
            doc = self.db_connect.db(app_name).doc(DocUploadRegister)
            data_item = doc.context.find_one(
                doc.fields.id == upload_id
            )
            if data_item is None:
                return -1
            else:
                chk = data_item[doc.fields.MsgCheckList] or {}
                self.memcache_service.set_dict(chk_key, dict([(k, v) for k, v in chk.items()]))
                chk_cache = chk

        return chk_cache.get(key.replace(".", "_")) or 0

    def make_local_path(self, app_name: str, upload_id: str, register_on: datetime.datetime,
                        file_ext: typing.Optional[str]):
        ext = file_ext or "unknown"
        if ext.startswith(".") and ext != "unknown":
            ext = ext[1:][0:3]
        return f"local://{app_name.lower()}/{register_on.year}/{register_on.month:02d}/{register_on.day:02d}/{ext}/{upload_id}"
