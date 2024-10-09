import pathlib
import sys
#/root/python-2024/lv-file-fix-2024/py-files-sv/cy_jobs/jobs/codx/codx_dm_file_info_list.py
sys.path.append(pathlib.Path(__file__).parent.parent.parent.parent.__str__())
import typing
from cyx.common import config
# setattr(config,"db_codx","mongodb://admin:Erm%402021@172.16.7.33:27017")
import cy_docs
from cy_jobs.jobs.codx.repositories import CodxRepository
import cy_kit.design_pattern
from cy_jobs.jobs.codx.lv_files_apps import AppList,ObjectInfo

@cy_kit.design_pattern.singleton()
class CodxWSComment(AppList):
    filter_file_name:str
    def __init__(self,filter_field_name:str,iter_version:str,app_name:str):
        super().__init__(app_name)
        self.iter_version = iter_version
        self.filter_field_name = filter_field_name
        fields = self.filter_field_name.split(".")
        self.filter_field = getattr(cy_docs.fields,fields[0])
        for x in fields[1:]:
            self.filter_field = getattr(self.filter_field,x)
        print(self.filter_field)
    def first_objects(self)->typing.Iterable[ObjectInfo]:
        while True:
            for app_name in self.apps():
                for item in self.get_items_by_app(app_name=app_name,recent=False):
                    yield item
    def last_objects(self)->typing.Iterable[ObjectInfo]:
        while True:
            for app_name in self.apps():
                for item in self.get_items_by_app(app_name=app_name, recent=True):
                    yield item
    def get_items_by_app(self, app_name:str,recent:bool)->typing.Iterable[ObjectInfo]:
        sort = CodxRepository.wp_comments.fields.CreatedOn.desc() if recent else CodxRepository.wp_comments.fields.CreatedOn.asc()
        agg = CodxRepository.wp_comments.tenant(app_name).context.aggregate().match(
            (self.filter_field==None)|(self.filter_field!=self.iter_version)
        ).sort(
            sort
        ).project(
            cy_docs.fields.object_id>>CodxRepository.wp_comments.fields.id

        ).limit(1)
        items = list(agg)
        if len(items)>0:
            ret = ObjectInfo()
            ret.Id = items[0].get('object_id')
            ret.AppName = app_name
            ret.DbContent = CodxRepository.wp_comments.tenant(app_name).context
            ret.FilterField = self.filter_field
            ret.Iter_version = self.iter_version
            yield ret



def main():
    a = CodxWSComment(filter_field_name="lv-files.ocr", iter_version="03", app_name="developer")

    for x in a.last_objects():
        dm_file_info_item = x.DbContent.find_one(cy_docs.fields._id== x.Id)
        print(dm_file_info_item)
        x.commit()
if __name__ =="__main__":
    main()






