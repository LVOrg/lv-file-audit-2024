import uuid

import cy_kit
import elasticsearch
from cyx.common import config
print(config)
client = elasticsearch.client.Elasticsearch(config.elastic_search.server)
import cy_es
index = "test-lv-docs"

id= str(uuid.uuid4())
# ret =cy_es.create_doc(
#     client=client,
#     id = id,
#     index=index,
#     body= dict(
#         pages=[
#             dict(
#                 page=0,
#                 conent="This is the test number one"
#
#             ),
#             dict(
#                 page=1,
#                 conent="This is the test number two"
#
#             ),
#             dict(
#                 page=2,
#                 conent="This is the final page"
#
#             )
#         ]
#     )
# )
expr= "fx search 'aaa' and fy=1"
import cy_es_x
ok = cy_es_x.Tree()
tx =ok.parse(expr)
print(tx)
field = cy_es.DocumentFields("pages").conent
fx = field >> "This is the test number one"
ret =cy_es.select(
    fields=["pages"],
    client=client,
    index=index,
    filter= fx,
    highlight_fields= ["pages.conent","pages.page"]
)
print(fx)