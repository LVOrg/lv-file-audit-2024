import pathlib
import sys
import traceback

sys.path.append(pathlib.Path(__file__).parent.parent.parent.__str__())
import cy_es.cy_es_manager as es_manager
from cyx.common import config
import elasticsearch

import typing
from cyx.repository import Repository
import cy_docs
from icecream import ic
from cyx.logs_to_mongo_db_services import LogsToMongoDbService
import cy_kit
class RemakeSearchService:
    logs = cy_kit.singleton(LogsToMongoDbService)
    def __init__(self):
        self.client = elasticsearch.Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=3600,
            sniff_timeout=30
        )
        self.__app_name = config.get("app_name") or "all"
    def do_remake(self,app_name:str):
        index_name = f"{config.elastic_search.prefix_index}_{app_name}"
        check_value = es_manager.check_is_allow_no_accent_content_setting(client=self.client,index= index_name)
        if check_value == 1:
            ic(f"{index_name} is ready for no accent search")
            return
        elif check_value == -1:
            ret =es_manager.create_index(client= self.client,index=index_name)
            print(ret)
        es_manager.close_index(client=self.client,index=index_name)
        es_manager.add_bm25_similarity(client=self.client,index=index_name)
        #fx=self.client.indices.get_mapping(index_name)
        #fx[index_name]['mappings']['properties']['content_vn']['analyzer']=='content_analyzer'
        #fx[index_name]['mappings']['properties']['content_vn']['similarity']=='bm25_similarity'
        #fx[index_name]['mappings']['properties']['content_vn']['fielddata']==True
        #fx[index_name]['mappings']['properties']['content_vn']['type']=='text'
        es_manager.create_no_accent_settings(
            client=self.client,
            index = index_name
        )
        es_manager.create_no_accent_mapping(
            client=self.client,
            index=index_name,
            field_name="content_vn"
        )
        es_manager.open_index(client=self.client, index=index_name)
        es_manager.remake_field(
            client=self.client,
            index=index_name,
            old_field="content",
            new_field="content_vn",
            timeout = "3600s"
        )
    def get_app_names(self) -> typing.List[str]:
        agg = Repository.apps.app("admin").context.aggregate().match(
            Repository.apps.fields.Name != config.admin_db_name
        ).match(
            Repository.apps.fields.AccessCount > 0
        ).sort(
            Repository.apps.fields.LatestAccess.desc()
        ).project(
            cy_docs.fields.app_name >> Repository.apps.fields.Name
        )
        ret = [x.app_name.lower() for x in agg]
        return ret
    def ge_app_names(self)->typing.List[str]:

        apps = self.get_app_names() if self.__app_name == "all" else [self.__app_name]
        return apps
    def do_remake_all(self):
        for app_name in self.ge_app_names():
            # if app_name!="developer":
            try:
                ic(f"{app_name} will be remake")
                self.do_remake(app_name)
                ic(f"{app_name} was remake")
            except:
                self.logs.log(
                    error_content=traceback.format_exc(),
                    url="ElasticSearch"
                )
                ic(f"{app_name} remake was fail")
                raise


if __name__ == "__main__":
    svc= RemakeSearchService()
    svc.do_remake_all()