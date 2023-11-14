import cy_kit
import elasticsearch
from cy_es import cy_es_manager
from cy_xdoc.services.search_engine import SearchEngine
se = cy_kit.singleton(SearchEngine)
es: elasticsearch.Elasticsearch =se.client
# mapping = cy_es_manager.get_mapping(client=es, index="lv-codx_lv-docs")
fx = cy_es_manager.update_mapping(client=es,index="lv-codx_lv-docs", data = dict(

))


for x in fx:
    print(x)

# Define the index and document type
