import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import datetime

import cy_es_x
from elasticsearch import Elasticsearch
from cy_xdoc.models.files import DocUploadRegister
client = Elasticsearch(hosts=["192.168.18.36:9200"])
index ="lv-codx_long-test-123"

filter=(cy_es_x.docs.mark_delete==False) & ((cy_es_x.docs.privileges.users.contains('hthan','tqcuong'))|(cy_es_x.docs.privileges.group.contains('nhom_a')))
import cy_kit
import cy_xdoc.services.search_engine
import cy_es
search_services:cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine)

# import cyx.rdr_segmenter.segmenter_services
# se = cy_kit.singleton(cyx.rdr_segmenter.segmenter_services.VnSegmenterService)
# fx = se.parse_word_segment("Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:",boot=[100])
# print(fx)
# fx = se.parse_word_segment("Chờ xét duyệt ".lower(),boot=[100])
# # filter1=None
# filter1 = {"$or":[{"1":{"$contains":["ADMIN"]}},{"U":{"$contains":["ADMIN"]}},{"9":{"$contains":[""]}},{"7":{"$contains":[""]}}]}
t= datetime.datetime.utcnow()
filter_0 = { "$eq": {"data_item.FileExt":"mp4"}}
filter = {
    "$and":[
        {
            "$ne":{"data_item":None}
        },{
            "$or":[
                    { "$eq": {"data_item.SizeInBytes":0}},
                    { "$eq": {"data_item.SizeInBytes":None}},
                ]
        }
    ]

}
filter_1 =(cy_es.DocumentFields("data_item").SizeInBytes==0) | (cy_es.DocumentFields("data_item").SizeInBytes==None)
ret=search_services.delete_by_conditional(
    app_name="test-2023",
    conditional=filter_0


)
if ret:
    print("OK")
else:
    print("Not found")
n= (datetime.datetime.utcnow()-t).total_seconds()
print(n)
# t= datetime.datetime.utcnow()
#
#
# ret=search_services.update_by_conditional(
#     app_name="test-2023",
#     conditional= (cy_es.DocumentFields("data_item").HasThumb==True) | (cy_es.DocumentFields("data_item").HasThumb==None) ,
#     data= {
#         "data_item":{
#
#              "UserProrFile_1":{
#                  "Name":"XXXX",
#                  "FullName":"Test"
#              }
#         }
#     }
#
# )
# if ret:
#     print("OK")
# else:
#     print("Not found")
# n= (datetime.datetime.utcnow()-t).total_seconds()
# print(n)
# fx= cy_es.create_filter_from_dict(filter1)
# ret = search_services.full_text_search(
#     app_name="hps-file-test",
#     privileges= filter1,
#     page_index=0,
#     content="404",
#     page_size=10,
#     highlight=False
#
# )
# hits = ret.hits
# total = hits.total
# for x in ret.items:
#     print(x)
# print(ret)



#
#
#     print(cls)

# fx = get_map(DocUploadRegister)





