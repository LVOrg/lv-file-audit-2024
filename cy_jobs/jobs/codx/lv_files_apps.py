import typing
import cy_docs
import cy_kit.design_pattern

from cyx.repository import Repository
from cyx.common import config
from cy_jobs.jobs.codx.repositories import get_available_tenants
from icecream import ic
class ObjectInfo:
    Id=None
    DbContent=None
    AppName = None
    FilterField = None
    Iter_version = None

    def commit(self):
        import pymongo.results
        if hasattr(self.DbContent,"update") and callable(self.DbContent.update):
            ret: pymongo.results.UpdateResult = self.DbContent.update(
                cy_docs.fields._id==self.Id,
                self.FilterField << self.Iter_version
            )

    def __repr__(self):
        return f"id={self.Id},tenant={self.AppName},filter_iter={self.FilterField==self.Iter_version}"

@cy_kit.design_pattern.singleton()
class AppList:
    def __init__(self,app_name:str):
        self.app_name = app_name
        self.app_agg = (Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name != config.admin_db_name
        ).match(
            {"Name": {"$in": get_available_tenants()}}
        )
        .match(
            (Repository.apps.fields.AccessCount > 0)
        ).sort(
            Repository.apps.fields.LatestAccess.desc()
        ).project(
            cy_docs.fields.app_name >> Repository.apps.fields.Name
        ))
    def apps(self)->typing.Iterable[str]:
        """
        Get all app_name in lv file admin manager
        @return:
        """

        if self.app_name=="all":
            items = list(self.app_agg)
            for x in items:
                yield x.app_name
        else:
            yield self.app_name

def main():
    apps_list = AppList(app_name="all")
    for x in apps_list.apps():
        print(x)
if __name__ == "__main__":
    main()