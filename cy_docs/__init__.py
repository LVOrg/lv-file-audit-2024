import os.path
import pathlib
import typing

import bson
import pymongo.mongo_client
import ctypes
import sys

__release_mode__ = True
__working_dir__ = pathlib.Path(__file__).parent.__str__()

sys.path.append(__working_dir__)
from cy_docs import cy_docs_x

from typing import TypeVar, Generic, List

T = TypeVar('T')

AggregateDocument = cy_docs_x.AggregateDocument


def expr(cls: T) -> T:
    """
    Create mongodb build expression base on __cls__
    :param cls:
    :return:
    """
    ret = cy_docs_x.fields[cls]

    return ret


def get_doc(collection_name: str, client: pymongo.mongo_client.MongoClient, indexes: List[str] = [],
            unique_keys: List[str] = []):
    return getattr(cy_docs_x, "Document")(collection_name, client, indexes=indexes, unique_keys=unique_keys)


def define(name: str, indexes: List[str] = [], uniques: List[str] = [],search:List[str]=[]):
    """
    Define MongoDb document
    The document infor is included : Name, Indexes, Unique Keys
    Xác định tài liệu MongoDb
    Thông tin tài liệu bao gồm: Tên, Chỉ mục, Khóa duy nhất
    Note: A combine fields index ( also call multi fields Index) declare with comma between each field sucha as ['a,b','c'].
    The same way for Unique Index
    Lưu ý: Chỉ mục trường kết hợp (còn gọi là Chỉ mục nhiều trường) khai báo bằng dấu phẩy giữa mỗi trường, chẳng hạn như ['a,b','c'].
    Cách tương tự cho Unique Index
    :param name:
    :param indexes:
    :param uniques:
    :return:
    """
    return cy_docs_x.document_define(name, indexes, uniques,search)


fields = cy_docs_x.fields
"""
For any expression
"""

FUNCS = cy_docs_x.FUNCS


def context(client, cls):
    return cy_docs_x.context(client, cls)


def concat(*args): return cy_docs_x.Funcs.concat(*args)


def exists(field): return cy_docs_x.Funcs.exists(field)


def is_null(field): return cy_docs_x.Funcs.is_null(field)


def is_not_null(field): return cy_docs_x.Funcs.is_not_null(field)


def not_exists(field): return cy_docs_x.Funcs.not_exists(field)


DocumentObject = cy_docs_x.DocumentObject


def file_get(client: pymongo.MongoClient, db_name: str, file_id):
    return cy_docs_x.file_get(client, db_name, file_id)


async def file_get_async(client: pymongo.MongoClient, db_name: str, file_id):
    return await cy_docs_x.file_get_async(client, db_name, file_id)


async def get_file_async(client, db_name, file_id):
    return await cy_docs_x.get_file_async(client, db_name, file_id)


def create_file(client: pymongo.MongoClient, db_name, file_name, content_type: str, chunk_size, file_size):
    return cy_docs_x.create_file(
        client=client,
        file_size=file_size,
        chunk_size=chunk_size,
        file_name=file_name,
        db_name=db_name,
        content_type=content_type
    )


def file_chunk_count(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId) -> int:
    return cy_docs_x.file_chunk_count(
        client=client,
        db_name=db_name,
        file_id=file_id
    )


def file_add_chunk(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId, chunk_index: int,
                   chunk_data: bytes):
    return cy_docs_x.file_add_chunk(
        client=client,
        db_name=db_name,
        file_id=file_id,
        chunk_index=chunk_index,
        chunk_data=chunk_data
    )


def file_add_chunks(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId, data: bytes,
                    index_chunk: int = 0):
    return cy_docs_x.file_add_chunks(
        client=client,
        db_name=db_name,
        file_id=file_id,
        data=data,
        index_chunk=index_chunk
    )


def to_json_convertable(data, predict_content_handler=None):
    return cy_docs_x.to_json_convertable(data, predict_content_handler)


def file_get_iter_contents(client: pymongo.MongoClient, db_name: str, files_id: bson.ObjectId, from_chunk_index: int,
                           num_of_chunks: int):
    return cy_docs_x.file_get_iter_contents(
        client=client,
        db_name=db_name,
        files_id=files_id,
        from_chunk_index_index=from_chunk_index,
        num_of_chunks=num_of_chunks
    )


def get_file_info_by_id(client, db_name, files_id):
    return cy_docs_x.get_file_info_by_id(
        client=client,
        db_name=db_name,
        files_id=files_id
    )


DocumentObject = cy_docs_x.DocumentObject


def create_empty_pydantic(_type):
    import pydantic

    ret = pydantic.BaseModel()
    for k, v in _type.__annotations__.items():
        if hasattr(v, "__args__") and isinstance(v.__args__, tuple) and len(v.__args__) == 2 and v.__args__[1] == type(
                None):
            ret.__dict__[k] = None
        else:
            ret.__dict__[k] = v()
    return ret


Field = cy_docs_x.Field


def EXPR(expr):
    """
    Mongodb expr function use in case {$expr:{$gt:["$Grade1", "$Grade2"]}}
    :param fx:
    :return:
    """
    assert isinstance(expr, dict) or isinstance(expr, Field)
    if isinstance(expr, dict):
        ret = Field(expr)
        ret.__data__ = {
            "$expr": expr
        }
        return ret
    elif isinstance(expr, Field):
        ret = Field(init_value=expr.to_mongo_db_expr())
        ret.__data__ = {
            "$expr": expr.to_mongo_db_expr()
        }
        return ret
    else:
        raise Exception(f"{expr} is invalid data type, args in EXPR must be dict or cy_docs_x.Field")



queryable_doc = cy_docs_x.queryable_doc
from pymongo.mongo_client import MongoClient
from cy_docs.cy_docs_x import context


class DbQueryableCollection(Generic[T]):
    def __init__(self, cls, client: MongoClient, db_name: str):
        self.__cls__ = cls
        self.__client__ = client
        self.__db_name__ = db_name

    @property
    def context(self):
        """
        Query context full Mongodb Access
        :return:
        """
        ret = context(
            client=self.__client__,
            cls=self.__cls__
        )[self.__db_name__]
        return ret

    @property
    def fields(self) -> T:
        return cy_docs_x.fields[self.__cls__]
    def search(self,text_search):
        """
        query = { "$text": { "$search": "a time-traveling DeLorean" } }

        :param text_search:
        :return:
        """
        ret = Field("")
        ret.__data__ = {
            f"$text": {
                "$search":text_search,
                "$diacriticSensitive": True,
                "$language":"fr"
            }
        }

        return ret


class DbQueryable:
    def __init__(self, db_name: str, client: MongoClient):
        self.db_name = db_name
        self.client = client

    def get_document_context(self, cls: T) -> DbQueryableCollection[T]:
        return DbQueryableCollection[T](cls, self.client, self.db_name)


class MongoQueryable:
    def __init__(self, client: MongoClient):
        self.__client__ = client
        self.__cache__ = {}

    def get_db_context(self, db_name: str) -> DbQueryable:
        if self.__cache__.get(db_name) is None:
            self.__cache__[db_name] = DbQueryable(db_name)
        return self.__cache__[db_name]
