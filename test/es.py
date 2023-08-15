import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
import cy_es
filter = cy_es.natural_logic_parse(
    "(data_item.all()) search 'this is page 1'"
)
fx:cy_es.cy_es_x.DocumentFields = cy_es.create_filter_from_dict(filter)

fx = fx | (cy_es.DocumentFields("code")==1)

fx.__highlight_fields__ =["test_content.*"]

se= cy_kit.singleton(SearchEngine)
ret = cy_es.search(
    client=se.client,
    index= "lv-codx_lv-docs",
    filter= fx,
    highlight= {
    "require_field_match": True,
    "fields": {
      "test_content.*" : { "pre_tags" : ["<em>"], "post_tags" : ["</em>"] }
    }}
)
# se.update_data_fields(
#     app_name="lv-docs",
#     id = "3b96a75f-3ac2-4e3f-a06b-ffceb92378be",
#     data= {
#         "test_content":{
#             "page1":"this is page 1",
#             "page2":"this is page 2",
#             "page3":"this is page 3",
#             "page4":"this is page 4",
#         }
#     }
#
# )
# ret = se.full_text_search(
#     app_name= "lv-docs",
#     logic_filter= filter,
#     content=None,
#     page_size=10,
#     highlight=["pages.contents"],
#     privileges= None,
#     page_index=0
#
# )
print(ret)