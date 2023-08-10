import pathlib
import sys

import cy_es

sys.path.append(
    pathlib.Path(__file__).parent.parent.__str__()
)
import cy_kit
from  cy_xdoc.models.files import DocUploadRegister
from cy_xdoc.services.search_engine import SearchEngine
from cyx.common.es_utils import ElasticSearchUtilsService
search_engine = cy_kit.singleton(SearchEngine)
es_service = cy_kit.singleton(ElasticSearchUtilsService)
context = es_service.get_context("default")
settings = context.get_settings()
total_fields_limit = context.get_total_fields_limit()
similarity = context.get_similarity()

context.add_similarity(name="codx_search",b_k=(0,10))
context.add_similarity_fields(
    fields =[
        "codx_search.content",
        "codx_search.data_item.FileName"
    ],
    name = "codx_search",
    b_k=(0,10)
)
context.create_new_field_from_exist_field(source="content.keyword",dest="codx_search.content")
lst = context.select(
    filter = cy_es.DocumentFields("codx_search").content ==None,
    fields = ["_id"],
    page_size=1000
)
list_of_ids = search_engine.get_unfinished_doc(
    app_name="default",
    page_size=1000
)
