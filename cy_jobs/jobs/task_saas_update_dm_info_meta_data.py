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
import cy_kit.design_pattern
from cy_jobs.jobs.codx.codx_dm_file_info_list import CodxDMFileInfo,ObjectInfo
from cy_jobs.jobs.codx.repositories import CodxRepository
from retry import retry
@cy_kit.design_pattern.singleton()
class FixMetaData(CodxDMFileInfo):
    logs = cy_kit.single(LogsToMongoDbService)
    search_engine = cy_kit.singleton(SearchEngine)
    def __init__(self):
        if not hasattr(config,"version"):
            raise Exception(f"version was not found in config")
        if not hasattr(config,"app_name"):
            raise Exception(f"app_name was not found in config")
        if not hasattr(config,"db_codx"):
            print(f"warning: db_codx was not found in config use default config")
        super().__init__(
            filter_field_name=f"lv-file-service.{type(self).__name__}",
            iter_version = config.version,
            app_name = config.app_name
        )
        self.codx_files = CodxRepository.dm_file_info
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
    def get_codx_meta_by_upload_id(self,iter_item:ObjectInfo):
        meta_data_agg = iter_item.DbContent.aggregate().match(
            CodxRepository.dm_file_info.fields.id==iter_item.Id
        ).project(
            CodxRepository.dm_file_info.fields.FileName,
            CodxRepository.dm_file_info.fields.FileSize,
            CodxRepository.dm_file_info.fields.Permissions,
            CodxRepository.dm_file_info.fields.UploadId,
            CodxRepository.dm_file_info.fields.CreatedBy,
            CodxRepository.dm_file_info.fields.CreatedOn,
            CodxRepository.dm_file_info.fields.FolderPath,
            CodxRepository.dm_file_info.fields.ObjectType,
            CodxRepository.dm_file_info.fields.ObjectID
        )


        items = list(meta_data_agg)
        if len(items)>0:
            return items[0]
        else:
            return None
    def convert_codx_meta(self,codx_meta):
        meta_data = {
            "FolderPath": codx_meta[self.codx_files.fields.FolderPath] or "",
            "EntityName": codx_meta[self.codx_files.fields.ObjectType] or "",
            "FileName": codx_meta[self.codx_files.fields.FileName] or "",
            "CreatedBy": codx_meta[self.codx_files.fields.CreatedBy] or "",
            "FileSize": codx_meta[self.codx_files.fields.FileSize] or 0,
            "ObjectID": codx_meta[self.codx_files.fields.ObjectID] or "",
            "ObjectType": codx_meta[self.codx_files.fields.ObjectType] or ""
        }
        return meta_data
    def convert_codx_privileges(self,codx_meta):
        server_privileges = self.make_privileges(codx_meta[self.codx_files.fields.Permissions])

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
        return client_privileges,server_privileges
    def re_update_meta_to_upload(self,upload_id:str,app_name:str,meta_data,client_privileges,server_privileges):
        """
        Re update meta data to upload file
        @param upload_id:
        @param codx_meta:
        @return:
        """

        data_item = Repository.files.app(app_name).context.find_one(
            Repository.files.fields.Id == upload_id
        )
        if data_item is None:
            ic(f"can not update metat data {app_name}, id= {upload_id}")
            return
        ret = Repository.files.app(app_name).context.update(
            Repository.files.fields.Id == upload_id,
            Repository.files.fields.meta_data << meta_data,
            Repository.files.fields.Privileges << client_privileges,
            Repository.files.fields.ClientPrivileges << server_privileges
            # Repository.files.fields.SyncFromPath
        )
        if ret.matched_count==0:
            ic(f"can not update meta data {app_name}, id= {upload_id}")
        else:
            ic(f"update meta data {app_name}, id= {upload_id} is Ok")


        import elasticsearch.exceptions
        @retry(tries=10,delay=5,exceptions=(elasticsearch.exceptions.RequestError))
        def do_update():
            self.search_engine.create_or_update_privileges(
                app_name=app_name,
                upload_id=upload_id,
                data_item=data_item,
                privileges=server_privileges,
                meta_info=meta_data,
                force_replace=True

            )
        try:
            do_update()
        except elasticsearch.exceptions.RequestError:
            self.logs.log(
                error_content=traceback.format_exc(),
                url=f"{app_name}/{upload_id}"
            )

if __name__ == "__main__":
    fix_meta_data = FixMetaData()
    for x in fix_meta_data.last_objects():
        ic(x)
        codx_meta = fix_meta_data.get_codx_meta_by_upload_id(x)
        if not codx_meta:
            x.commit()
            continue
        if not codx_meta.get("UploadId"):
            x.commit()
            continue
        meta_data = fix_meta_data.convert_codx_meta(codx_meta)
        client_privileges, server_privileges =fix_meta_data.convert_codx_privileges(codx_meta)
        fix_meta_data.re_update_meta_to_upload(
            upload_id = codx_meta.get("UploadId"),
            app_name = x.AppName,
            meta_data =meta_data,
            server_privileges = server_privileges,
            client_privileges = client_privileges
        )
        x.commit()
#python cy_jobs/jobs/task_saas_update_dm_info_meta_data.py version=v-01 db_codx=mongodb://admin:Erm%402021@172.16.7.33:27017 app_name=all