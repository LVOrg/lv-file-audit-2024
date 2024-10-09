import hashlib
import os.path
import time
import typing

from icecream import ic

from cyx.repository import Repository
from cyx.common import config
import cy_docs
import cy_file_cryptor.context
cy_file_cryptor.context.set_server_cache(config.cache_server)
class UploadInfo:
    upload_id:str
    uri_file_path:str
    physical_path: str
    output_dir:str
    app_name:str
    filter_field=None
    filter_value:str
    def commit(self):
        if not self.filter_field:
            return
        Repository.files.app(self.app_name).context.update(
            Repository.files.fields.id == self.upload_id,
            self.filter_field << self.filter_value

        )

    def decrypt_file(self)->str:
        decrypt_file_name = hashlib.sha256(self.physical_path.encode()).hexdigest()
        decrypt_file_path = os.path.join(self.output_dir,f"{decrypt_file_name}.{self.filter_value}")
        if os.path.isfile(decrypt_file_path):
            return decrypt_file_path
        else:
            with open(self.physical_path,"rb") as fs:
                with open(decrypt_file_path,"wb") as wb:
                    data = fs.read()
                    if isinstance(data,str):
                        data = data.encode()
                    wb.write(data)
                    return decrypt_file_path


class ListAllFilesService:
    def __init__(self):
        self.storage_path  = config.file_storage_path.replace('/',os.sep)
        self.storage_path_decrypt = os.path.join(self.storage_path,f"__{type(self).__module__}_{type(self).__name__}")
        os.makedirs(self.storage_path_decrypt,exist_ok=True)
    def get_apps(self,app_name:str="all")->typing.Iterable[str]:
        if app_name!="all":
            yield app_name
        else:
            agg = Repository.apps.app("admin").context.aggregate().match(
                Repository.apps.fields.Name != config.admin_db_name
            ).match(
                Repository.apps.fields.AccessCount > 0
            ).sort(
                Repository.apps.fields.LatestAccess.desc()
            ).project(
                cy_docs.fields.app_name >> Repository.apps.fields.Name
            )
            ic(agg)
            lst_items = [x.app_name.lower() for x in agg]
            for x in lst_items:
                yield x
    def get_files(self,
                 file_type:typing.Union[str,typing.List[str]],
                 app_name:str="all",
                  recent:bool=True,
                 filter_field_name:typing.Optional[str]=None,
                 filter_value:typing.Optional[str]=None)->typing.Iterable[UploadInfo]:
        sort_by = Repository.files.fields.RegisterOn.desc() if recent else Repository.files.fields.RegisterOn.asc()
        filter = (Repository.files.fields.Status>0)
        filter_field = None
        if isinstance(file_type,str):
            filter = filter & (Repository.files.fields.FileExt==file_type)
        elif isinstance(file_type,list):
            filter = filter & { Repository.files.fields.FileExt.__name__ :{"$in":file_type}}
        if filter_field_name and filter_value:
            filter_field = getattr(cy_docs.fields,filter_field_name)
            filter = filter & ((filter_field==None)|(filter_field!=filter_value))

        for _app_name in self.get_apps(app_name):
            agg = Repository.files.app(_app_name).context.aggregate().match(
                filter
            ).sort(
                sort_by
            ).project(
                cy_docs.fields.upload_id>> Repository.files.fields.id,
                cy_docs.fields.uri_file_path >> Repository.files.fields.MainFileId
            ).limit(1)
            ic(_app_name,agg)
            items = list(agg)
            if len(items)>0:
                item = items[0]
                if not isinstance(item.uri_file_path,str):
                    self.__commit__(
                        app_name  =_app_name,
                        filter = Repository.files.fields.id==item.upload_id,
                        updater = filter_field << filter_value
                    )
                    ic(f"{_app_name}, id={item.upload_id} commit")
                    continue
                elif not "://" in item.uri_file_path:
                    self.__commit__(
                        app_name=_app_name,
                        filter=Repository.files.fields.id == item.upload_id,
                        updater=filter_field << filter_value
                    )
                    ic(f"{_app_name}, id={item.upload_id} commit")
                    continue
                ret_obj  = UploadInfo()
                ret_obj.physical_path = os.path.join(self.storage_path,item.uri_file_path.split("://")[1])
                if not os.path.isfile(ret_obj.physical_path):
                    self.__commit__(
                        app_name=_app_name,
                        filter=Repository.files.fields.id == item.upload_id,
                        updater=filter_field << filter_value
                    )
                    continue
                ret_obj.app_name =_app_name
                ret_obj.filter_field = filter_field
                ret_obj.filter_value = filter_value
                ret_obj.upload_id = item.upload_id
                ret_obj.output_dir = self.storage_path_decrypt
                yield ret_obj

    def __commit__(self, app_name, filter, updater):
        Repository.files.app(app_name).context.update(
            filter,
            updater
        )

if __name__ == "__main__":
    fx = ListAllFilesService()
    while True:
        iter_info = fx.get_files(
            file_type="pdf",
            filter_field_name="long-test",
            filter_value="v-03",
            app_name="developer"
        )
        for x in iter_info:
            ic(x.__dict__)
            x.commit()
        time.sleep(0.2)

