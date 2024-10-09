import cy_es.cy_es_manager as es_manager
from cyx.common import config
import elasticsearch
from pymongo import timeout


class RemakeSearchService:
    def __init__(self):
        self.client = elasticsearch.Elasticsearch(
            hosts=config.elastic_search.server,
            timeout=3600,
            sniff_timeout=30
        )
    def do_remake(self,app_name:str):
        index_name = f"{config.elastic_search.prefix_index}_{app_name}"
        es_manager.close_index(client=self.client,index=index_name)
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
            timeout = "10m"
        )

if __name__ == "__main__":
    svc= RemakeSearchService()
    svc.do_remake("lv-docs")