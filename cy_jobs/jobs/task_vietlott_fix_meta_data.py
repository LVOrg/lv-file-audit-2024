import sys
import pathlib
import time
import traceback
import typing

from icecream import ic



working_dir=pathlib.Path(__file__).parent.parent.parent.__str__()
ic(f"working dir={working_dir}")
sys.path.append(working_dir)
sys.path.append("/app")
import cy_kit
from cyx.common import config
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
from cyx.repository import Repository
import cy_docs
from cy_xdoc.services.search_engine import SearchEngine
class FixMetaData:
    logs = cy_kit.single(LogsToMongoDbService)
    search_engine = cy_kit.singleton(SearchEngine)
    def __init__(self):
        self.app_name = config.get("app_name") or "default"
        self.codx_db = config.codx_db
        self.meta_version = config.meta_version
        self.meta_update_mark_field =getattr(cy_docs.fields,"meta_update_mark")
        self.filter = (self.meta_update_mark_field==None)|(self.meta_update_mark_field!=self.meta_version)
        self.codx_files = Repository.codx_dm_file_info.app(self.codx_db)
        self.time_interval= config.get("time_interval") or 5
        ic(self.filter)

    def make_privileges(self,permissions):
        """
        This methdo convert permissions from codx into privileges of ES
        :param permissions:
        :return:
        """

        if not permissions:
            return {}

        es_privileges = [{(x.get("ObjectType") or "").lower(): [(x.get("ObjectID") or "").lower()]} for x in
                         permissions]
        return es_privileges

    def get_latest_upload_id(self)->typing.Optional[str]:
        """
        Get upload_id of latest upload
        """
        agg = Repository.files.app(self.app_name).context.aggregate().sort(
            Repository.files.fields.RegisterOn.desc()
        ).match(
            self.filter
        ).project(
            cy_docs.fields.upload_id>>Repository.files.fields.id
        ).limit(1)
        ic(agg)
        items = list(agg)
        if len(items)>0:
            ret = items[0].upload_id
            Repository.files.app(self.app_name).context.update(
                Repository.files.fields.id==ret,
                self.meta_update_mark_field << self.meta_version
            )
            return ret
        return None

    def get_codx_meta_by_upload_id(self,upload_id:str):
        meta_data_agg = self.codx_files.context.aggregate().match(
            Repository.codx_dm_file_info.fields.UploadId==upload_id
        ).project(
            self.codx_files.fields.FileName,
            self.codx_files.fields.FileSize,
            self.codx_files.fields.Permissions,
            self.codx_files.fields.UploadId,
            self.codx_files.fields.CreatedBy,
            self.codx_files.fields.CreatedOn,
            self.codx_files.fields.FolderPath,
            self.codx_files.fields.ObjectType,
            self.codx_files.fields.ObjectID
        )
        ic(meta_data_agg)
        items = list(meta_data_agg)
        if len(items)>0:
            return items[0]
        else:
            return None

    def re_update_meta_to_upload(self,upload_id:str,codx_meta):
        """
        Re update meta data to upload file
        @param upload_id:
        @param codx_meta:
        @return:
        """
        server_privileges = self.make_privileges(codx_meta[self.codx_files.fields.Permissions])
        meta_data = {
            "FolderPath": codx_meta[self.codx_files.fields.FolderPath] or "",
            "EntityName": codx_meta[self.codx_files.fields.ObjectType] or "",
            "FileName": codx_meta[self.codx_files.fields.FileName] or "",
            "CreatedBy": codx_meta[self.codx_files.fields.CreatedBy] or "",
            "FileSize": codx_meta[self.codx_files.fields.FileSize] or 0,
            "ObjectID": codx_meta[self.codx_files.fields.ObjectID] or "",
            "ObjectType": codx_meta[self.codx_files.fields.ObjectType] or ""
        }
        if not {"1": [codx_meta.CreatedBy.lower()]} in server_privileges:
            server_privileges += [{"1": [codx_meta.CreatedBy.lower()]}]
        if not {"7": [""]} in server_privileges:
            server_privileges += [{"7": [""]}]
        client_privileges = {}

        for px in server_privileges:
            for k, v in px.items():
                if client_privileges.get(k) is None:
                    client_privileges[k] = []
                client_privileges[k] += v
        Repository.files.app(self.app_name).context.update(
            Repository.files.fields.Id == upload_id,
            Repository.files.fields.meta_data << meta_data,
            Repository.files.fields.Privileges << client_privileges,
            Repository.files.fields.ClientPrivileges << server_privileges,
            Repository.files.fields.UpdateMetaDataTime << self.meta_version,
            # Repository.files.fields.SyncFromPath
        )
        data_item = Repository.files.app(self.app_name).context.find_one(
            Repository.files.fields.Id == upload_id
        )
        self.search_engine.create_or_update_privileges(
            app_name=self.app_name,
            upload_id=upload_id,
            data_item=data_item,
            privileges=server_privileges,
            meta_info=meta_data,
            force_replace=True

        )
    def do_update(self):
        try:
            upload_id = self.get_latest_upload_id()
            if not upload_id:
                return
            codx_meta = self.get_codx_meta_by_upload_id(upload_id)
            if not codx_meta:
                return
            self.re_update_meta_to_upload(
                upload_id=upload_id,
                codx_meta=codx_meta
            )

        except:
            self.logs.log(
                error_content=traceback.format_exc(),
                url=f"upload={upload_id or 'not found'}"
            )

if __name__ == "__main__":
    svc= cy_kit.singleton(FixMetaData)
    while True:
        time.sleep(config.get("time_interval") or 5)
        svc.do_update()
