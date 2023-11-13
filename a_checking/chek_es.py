import cy_kit
import elasticsearch
from cy_es import cy_es_manager
from cy_xdoc.services.search_engine import SearchEngine
se = cy_kit.singleton(SearchEngine)
es: elasticsearch.Elasticsearch =se.client
mapping = cy_es_manager.get_mapping(client=es, index="lv-codx_lacvietdemo")
keyword_fields = cy_es_manager.get_all_keyword_fields(client=es, index="lv-codx_lacvietdemo")
index = es.indices.get(
    index="lv-codx_lacvietdemo",
    # ignore=400,
    # body={
    #     "mappings": {
    #         "properties": {
    #             "content_raw_text": {
    #                 "type": "text"
    #             }
    #         }
    #     }
    # }
)
es.indices.put_mapping(
    index='lv-codx_lacvietdemo',
    body={
        "properties":{
            "data_item.FileName_raw_text":{
                "fielddata" : True,
                "type" : "text"
            }
        }
    }
)



# Define the index and document type
