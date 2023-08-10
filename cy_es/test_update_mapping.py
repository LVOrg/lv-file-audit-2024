import datetime
import time

from setuptools.command.rotate import rotate
from cy_xdoc.models.files import DocUploadRegister
import cy_es
import elasticsearch
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.files import FileServices
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
import cy_es

se = cy_kit.singleton(SearchEngine)
fs = cy_kit.singleton(FileServices)
vn = cy_kit.singleton(VnSegmenterService)
client = elasticsearch.Elasticsearch(
    hosts=["192.168.18.36:9200"]
)
index = f"lv-codx_test-2023"
fx = cy_es.DocumentFields("data_item")
emp = cy_es.DocumentFields("Employee")
vx = (fx._id @ "f25609d2-7365-4c49-a0f3-a17aa229ec51") | (fx._id @ "3c2b3749-b0a4-4c3e-9723-aeb5da97eb19")
map = cy_es.get_map_struct(client,index)

filter1 = {
    "$$search":{
        "$fields":["data_item.Filename"],
        "$value":"long test"
    }

}
fx=cy_es.create_filter_from_dict(filter1)
print(fx)