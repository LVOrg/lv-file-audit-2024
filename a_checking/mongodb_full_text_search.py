import datetime
import sys
import typing
import uuid

import cy_docs
from cy_docs import context,DbQueryable
app="developer"
@cy_docs.define(
    name="lv-file-search-dev-0010",
    search=["content"]
)
class Test:
    content: typing.List[str]|None
from typing import Generic, TypeVar
T = TypeVar('T')
import json
from mongoengine import (
    Document,
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
    FloatField,
    DynamicField, ObjectIdField, ListField,EmbeddedDocumentField


)
import datetime,types
import bson.objectid

from mongoengine import Document, EmbeddedDocument, StringField, IntField, Q

class Address(EmbeddedDocument):
    city = StringField()
    zipcode = IntField()

class Person(Document):
    name = StringField()
    address = EmbeddedDocumentField(Address)
@cy_docs.define(
    name="lv-file-search-dev-test-1",
    search=["content"]
)
class TestSearch:
    Code:str
    Name:str
    # class SubClass:
    #     text_field: str
    #     date_field: datetime.datetime
    #     int_field: int
    #     bool_field: bool
    #     float_field: float
    #     dict_field: dict
    # sub_field: SubClass
    # text_field: str
    # date_field: datetime.datetime
    # int_field: int
    # bool_field: bool
    # float_field: float
    # dict_field: dict
    # list_text: typing.List[str]
    # list_int: typing.List[int]
    # list_date: typing.List[datetime.datetime]
    # list_bool: typing.List[bool]
    # list_float: typing.List[float]
    # op_id: bson.ObjectId|None
    # op_text_field: str|None
    # op_date_field: datetime.datetime|None
    # op_int_field: int|None
    # op_bool_field: bool|None
    # op_float_field: float|None
    # op_dict_field: dict|None
import functools
class User(Document):
    first_name = StringField(required=True)
    last_name = StringField(required=True)

    age = IntField(min_value=0)

# Create a user instance
from mongoengine import connect
from cyx.common import config
connect(host= config.db)
# connect(config.db)
from cyx.repository import DocUploadRegister
# user.validate()
from cy_docs.cy_engine import __extract_annotations_from_class__,__create_coll_from_dict__,get_coll
from mongoengine import Q



@cy_docs.define(
    name="long-test-005",
    indexes=["Code,Name","Name"],
    uniques=["Code"]
)
class LongTest:
    Code:str
    Name:str
    Address: str|None

    class ClsDept:
        Code: str
        Name: str
    Dept: ClsDept

coll= get_coll(LongTest)

x=coll(Code="B",Name="AAA",Dept=coll.Dept(Code="1",Name="A"))

x.save()
# field = __extract_annotations_from_class__(TestSearch)
# cls = __create_coll_from_dict__(field,col_name="long-test-full-text-search")
# fx=cls(Code="AAA",Name="Test")
# # fx.validate()
# fx.save()
from mongoengine import (
    Document,
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
    FloatField,
    DynamicField, ObjectIdField, ListField


)
from  mongoengine.base import ComplexBaseField,BaseField, BaseDict

# def get_coll(cls:T,col_name:str=None)->T:
#     class RetCls(Document):
#         pass
#     info_dict=dict(
#         doc_name = cls.__document_name__,
#         doc_index = cls.__document_indexes__,
#         doc_unique_index = cls.__document_unique_keys__,
#         doc_search_fields = cls.__document_search_fields__
#     )
#     doc_annotations = cls.__annotations__
#     fields=__extract_annotations__(doc_annotations)
#     return cls
# fx= get_coll(DocUploadRegister)






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
        (cy_docs.fields.migrate_from_es==None) | (cy_docs.fields.migrate_from_es!=11)
    ).project(
        cy_docs.fields.upload_id>>cy_docs.fields._id
    ).limit(100)
    lst = list(docs)
    for x in lst:
        es_doc = get_doc(es_client,index=f"lv-codx_{app}",id=x.upload_id)
        if es_doc!=None:
            if hasattr(es_doc.source,"content") and isinstance(es_doc.source.content,str):
                content = es_doc.source.content
                content = content.replace('\r','\n')
                paragraphs = content.split('.')
                reduce_paragraphs =[]
                list_size = sys.getsizeof(reduce_paragraphs)
                for paragraph in paragraphs:
                    txt_content = paragraph
                    for c in ['\n','\t','\r']:
                        txt_content = txt_content.replace(c,' ')
                    txt_content = txt_content.rstrip(" ").lstrip(" ")
                    while "  " in txt_content:
                        txt_content = txt_content.replace("  "," ")
                    if list_size+sys.getsizeof(txt_content)>15000000:
                        break
#                     if len(txt_content)>0:
#                         reduce_paragraphs+=[txt_content]
#                     list_size += sys.getsizeof(txt_content)
#
#                 docs_search.context.insert_one(
#                     docs_search.fields.Id << x.upload_id,
#                     docs_search.fields.content << reduce_paragraphs
#                 )
#
#
#         Repository.files.app(app).context.update(
#             Repository.files.fields.Id==x.upload_id,
#             cy_docs.fields.migrate_from_es<<11
#         )
#     print(f"Lines= {len(lst)}")
#
# # get_doc()
# # qr = DbQueryable("lv-docs",client)
# # docs = qr.get_document_context(Test)
# # text=(f"Kinh goi:.......Ban Lãnh Đạo ................................................................................................,"
# #       f"Ho và ten người đề nghị thanh toán:....Tran Đinh Thang.......................................................,"
# #       f"Bộ phận (Hoặc địa chỉ):...Mua hàng.......................................................................................,"
# #       f"Nội dung thanh toán:..Thanh toán cho nhà cung cấp: CÔNG TY CỔ PHẦN ĐỒNG NAI,"
# #       f"theo đơn hàng mua số: PO002. Ngày: 01/05/2024................................................................,"
# #       f"Số tiền: 71.280.000........ (Viết bằng chữ):.. Bảy mươi triệu hai trăm tám mươi ngàn đồng.,"
# #       f"(Kèm theo ..HD0003................... chứng từ gốc")
# # for x in text.split(','):
# #     docs.context.insert_one(
# #         docs.fields.content<<x
# #     )
# #
# # # for x in docs.context.find({}):
# # #     print(x)
# for i in range(0,10):
#     t=datetime.datetime.utcnow()
#     # agg=docs_search.context.find(
#     #     docs_search.search("MẪU THÔNG BÁO "),linmit=10
#     # )
#     agg = docs_search.context.aggregate().match(
#             docs_search.search("MẪU THÔNG BÁO ")
#     ).project(
#         cy_docs.fields.score>>{ "$meta": "textScore" },
#         docs_search.fields.id
#     ).sort(
#         cy_docs.fields.score.desc()
#     ).limit(10)
#     ls = list(agg)
#     n = datetime.datetime.utcnow() - t
#     print(n.total_seconds())
#     print("Xong")
#     for x in ls:
#         print(x)
#
#
# from cyx.repository import Repository