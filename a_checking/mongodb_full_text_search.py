import datetime
import typing

import cy_docs
from cy_docs import context,DbQueryable
app="developer"
@cy_docs.define(
    name="lv-file-search-dev",
    search=["content"]
)
class Test:
    content: typing.List[str]
from pymongo.mongo_client import MongoClient
uri="mongodb://admin-doc:123456@192.168.18.36:27017/lv-docs"
uri_es= "http://192.168.18.36:9200"
from elasticsearch.client import Elasticsearch
es_client = Elasticsearch(uri_es)
client= MongoClient(uri)
from cyx.repository import Repository
from cy_es import get_doc
lst=[1]
qr = DbQueryable(app,client)
docs_search = qr.get_document_context(Test)
while len(lst)>0:
    docs = Repository.files.app(app).context.aggregate().match(
        (cy_docs.fields.migrate_from_es==None) | (cy_docs.fields.migrate_from_es!=6)
    ).project(
        cy_docs.fields.upload_id>>cy_docs.fields._id
    ).limit(100)
    lst = list(docs)
    for x in lst:
        es_doc = get_doc(es_client,index=f"lv-codx_{app}",id=x.upload_id)
        if es_doc!=None:
            if hasattr(es_doc.source,"content") and isinstance(es_doc.source.content,str):
                content = es_doc.source.content
                for c in ['\n','\t','\r']:
                    content = content.replace(c,' ')
                content = content.rstrip(" ").lstrip(" ")
                while "  " in content:
                    content = content.replace("  "," ")
                docs_search.context.insert_one(
                    docs_search.fields.Id << x.upload_id,
                    docs_search.fields.content << content[0:(16777216//2)-100]
                )


        Repository.files.app(app).context.update(
            Repository.files.fields.Id==x.upload_id,
            cy_docs.fields.migrate_from_es<<6
        )
    print(f"Lines= {len(lst)}")

# get_doc()
# qr = DbQueryable("lv-docs",client)
# docs = qr.get_document_context(Test)
# text=(f"Kinh goi:.......Ban Lãnh Đạo ................................................................................................,"
#       f"Ho và ten người đề nghị thanh toán:....Tran Đinh Thang.......................................................,"
#       f"Bộ phận (Hoặc địa chỉ):...Mua hàng.......................................................................................,"
#       f"Nội dung thanh toán:..Thanh toán cho nhà cung cấp: CÔNG TY CỔ PHẦN ĐỒNG NAI,"
#       f"theo đơn hàng mua số: PO002. Ngày: 01/05/2024................................................................,"
#       f"Số tiền: 71.280.000........ (Viết bằng chữ):.. Bảy mươi triệu hai trăm tám mươi ngàn đồng.,"
#       f"(Kèm theo ..HD0003................... chứng từ gốc")
# for x in text.split(','):
#     docs.context.insert_one(
#         docs.fields.content<<x
#     )
#
# # for x in docs.context.find({}):
# #     print(x)
for i in range(0,10):
    t=datetime.datetime.utcnow()
    # agg=docs_search.context.find(
    #     docs_search.search("MẪU THÔNG BÁO "),linmit=10
    # )
    agg = docs_search.context.aggregate().match(
            docs_search.search("MẪU THÔNG BÁO ")
    ).project(
        cy_docs.fields.score>>{ "$meta": "textScore" },
        docs_search.fields.id
    ).limit(10)
    ls = list(agg)
    n = datetime.datetime.utcnow() - t
    print(n.total_seconds())
    print("Xong")
    for x in ls:
        print(x)


from cyx.repository import Repository