"""
cy_docs is library for mongodb document manipulating such as:
1-binary mongodb expression builder:
    Example: print(cy_docs.fields.code=='001' and cy_docs.fields.age>18)

find, find_one, find_async, find_one_async
Example:
    __client__ = pymongo.mongo_client.MongoClient(host=..,port=..,..)
    my_doc = cy_docs.get_doc(
        "my-docs",
         __client__
        )
    ret =my_doc['my-db'].insert_one(cy_docs.fields.code<<'001',cy_docs.fields.age<<32)
    print (ret)
Special:
    ret =my_doc['my-db'].insert_one(cy_docs.fields.code<<'001',cy_docs.fields.age<<32) can be changed
    ret =my_doc['my-db']<<(cy_docs.fields.code<<'001',cy_docs.fields.age<<32)
    find_item =my_doc['my-db'].find_one(cy_docs.fields.code=='001' & cy_docs.fields.age == 32) can be changed
    find_item =my_doc['my-db']@(cy_docs.fields.code=='001' & cy_docs.fields.age == 32) can be changed
    find_items = my_doc['my-db'].find(cy_docs.fields.code!='001' & cy_docs.fields.age < 32) can be changed
    find_items = my_doc['my-db']>>(cy_docs.fields.code!='001' & cy_docs.fields.age < 32) can be changed
"""
import asyncio
import threading
import typing

import pydantic
from datetime import datetime


def get_version() -> str:
    import os
    return f"0.0.4{os.path.splitext(__file__)[1]}"


import datetime
import json
import uuid
from typing import List, Union
from re import Pattern, IGNORECASE
import bson

import inspect
import re
import pymongo.mongo_client
import gridfs


def get_mongodb_text(data):
    if isinstance(data, dict):

        ret = {}
        for k, v in data.items():
            ret[k] = get_mongodb_text(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [get_mongodb_text(x)]
        return ret
    elif isinstance(data, str):
        return data
    elif isinstance(data, datetime.datetime):
        return data
    elif isinstance(data, uuid.UUID):
        return data.__str__()
    elif isinstance(data, int):
        return data
    elif isinstance(data, float):
        return data
    elif isinstance(data, complex):
        return dict(
            imag=data.imag,
            real=data.real
        )
    elif isinstance(data, bson.ObjectId):
        return f"ObjectId({data.__str__()})"
    elif isinstance(data, Pattern):
        if (data.flags & IGNORECASE).value != 0:
            return {"$regex": f"{data.pattern}/i"}
        else:
            return {"$regex": data.pattern}
    elif hasattr(type(data), "__str__"):
        fn = hasattr(type(data), "__str__")
        if callable(fn):
            return data.__str__()
        else:
            return data
    else:
        try:
            ret = data.__str__()
            return ret
        finally:
            return data


__hash_check_dict__ = {}
__hash_check_dict_lock__ = threading.Lock()

__camel_cache__ = {}
__camel_lock__ = threading.Lock()


def to_camel(name: str) -> str:
    if name.lower() == "id":
        return "_id"
    if __camel_cache__.get(name):
        return __camel_cache__[name]
    with __camel_lock__:
        ret = ""
        pos = 0
        for c in name:
            if c.isupper():
                if pos == 0:
                    ret += f"{c.lower()}"
                else:
                    ret += f"_{c.lower()}"
            else:
                ret += c
            pos += 1
        __camel_cache__[name] = ret
    return __camel_cache__[name]


def camel_dict(data: dict) -> dict:
    ret = {}
    for k, v in data.items():
        if k[0:2] == "__" and k[:-2] == "__":
            continue
        if hasattr(v, "__annotations__") and isinstance(v.__annotations__, dict):
            d = camel_dict(v.__annotations__)
            d["__name__"] = k
            if hasattr(v, "__module__"):
                d["__module__"] = v.__module__
            if hasattr(v, "__name__"):
                d["__module__"] = v.__name__
            ret[to_camel(k)] = d
        elif not isinstance(v, dict):
            ret[to_camel(k)] = k
        else:
            ret[to_camel(k)] = camel_dict(v)
    return ret


def convention_get(hash_key: str, name: str):
    if name.lower() == "id":
        return "_id"
    global __hash_check_dict__
    if __hash_check_dict__.get(hash_key) is None:
        return None
    data = __hash_check_dict__[hash_key]
    return data.get(to_camel(name))


class __BaseField__:
    def __init__(self, init_value: Union[str, dict, type], oprator: str = None):
        if hasattr(init_value, "__annotations__") and isinstance(init_value.__annotations__, dict):
            self.__set_check__(init_value)
            return
        self.__name__ = None
        self.__data__ = None
        self.__agg__function_call__ = None
        self.__oprator__ = oprator
        if isinstance(init_value, str):
            self.__name__ = init_value
        elif isinstance(init_value, dict):
            self.__data__ = init_value
        elif isinstance(init_value, Field):
            self.__data__ = init_value.to_mongo_db()
        else:
            raise Exception("init_value must be str or dict")
        self.__check_map__module__ = None
        self.__check_map__name__ = None
        self.__check_constraint__ = {}

    def __set_check__(self, cls):
        global __hash_check_dict__
        self.__delegate_type__ = cls
        if isinstance(cls, dict):
            self.__check_map__module__ = cls["__module__"]
            self.__check_map__name__ = cls["__name__"]
            hash_key = f"{self.__check_map__module__}/{self.__check_map__name__}"
            if not __hash_check_dict__.get(hash_key):
                with __hash_check_dict_lock__:
                    __hash_check_dict__[hash_key] = camel_dict(cls)
        elif hasattr(cls, "__module__"):
            self.__check_map__module__ = cls.__module__
            self.__check_map__name__ = cls.__name__
            hash_key = f"{self.__check_map__module__}/{self.__check_map__name__}"
            if not __hash_check_dict__.get(hash_key):
                with __hash_check_dict_lock__:
                    __hash_check_dict__[hash_key] = camel_dict(cls.__annotations__)

    def __getattr__(self, item):
        if item[0:2] != "__" and item[:-2] != "__" and self.__check_map__name__ is not None:
            hash_key = f"{self.__check_map__module__}/{self.__check_map__name__}"
            check_name = convention_get(hash_key, item)
            if check_name is None:
                raise AttributeError(
                    f"f{item} was not found in  {self.__check_map__module__}.{self.__check_map__name__}")
            else:
                return self.__dict__.get(check_name)
        return self.__dict__.get(item)

    def to_mongo_db(self) -> Union[str, dict]:
        if self.__data__ is not None:
            return self.__data__
        else:
            return self.__name__

    def to_mongo_db_expr(self) -> Union[str, dict]:
        if self.__data__ is not None:
            return self.__data__
        else:
            return "$" + self.__name__


class Field(__BaseField__):
    def __init__(self, init_value: Union[str, dict], oprator: str = None, is_expr=False):
        """
        Init a base field
        :param __name__:
        """
        __BaseField__.__init__(self, init_value, oprator)
        self.__value__ = None
        self.__has_set_value__ = False
        self.__alias__ = None
        self.__sort__ = 1
        self.__is_expr__ = is_expr

    def day(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$dayOfMonth": f"${ret.__name__}"

        }

        return ret

    def month(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$month": f"${ret.__name__}"

        }
        return ret

    def year(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$year": f"${ret.__name__}"

        }
        return ret

    def hour(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$hour": f"${ret.__name__}"

        }
        return ret

    def minute(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$minute": f"${ret.__name__}"

        }
        return ret

    def second(self):
        ret = Field(self.__name__)
        ret.__data__ = {
            "$second": f"${ret.__name__}"

        }
        return ret

    def reduce(self, data, reduce_type: type = None, skip_require: bool = False):
        import builtins
        reduce_type = reduce_type or self.__delegate_type__
        ret = {"_id": data.get("_id")}
        require_fields = []
        for k, v in reduce_type.__annotations__.items():
            try:
                ele_value = data.get(k)

                if hasattr(v, "__module__") and v.__module__ == "typing":

                    if str(v).startswith("typing.Union[") or str(v).startswith("typing.Optional["):
                        if ele_value is None:
                            if str(v).endswith(', NoneType]'):
                                ret[k] = None
                            else:
                                require_fields += [k]
                        else:
                            ret[k] = ele_value
                    elif ele_value is None:
                        require_fields += [k]
                    elif type(ele_value) != v.__origin__:
                        raise Exception(f"Can not cast {ele_value} to {v}")
                    else:
                        ret[k] = ele_value

                elif ele_value is None:
                    require_fields += [k]
                elif isinstance(v, str) and hasattr(builtins, v) and isinstance(ele_value, getattr(builtins, v)):
                    ret[k] = ele_value
                else:
                    try:
                        if isinstance(ele_value, v):
                            ret[k] = ele_value
                    except Exception as e1:
                        try:
                            ret[k] = v(ele_value)
                        except Exception as e:
                            ret[k] = ele_value
            except Exception as e:
                raise e

        if len(require_fields) > 0 and skip_require:
            str_require_fields_list = '\n\t'.join(require_fields)
            raise Exception(f"These below fields are require:\n {str_require_fields_list}\n"
                            f"Preview file {inspect.getfile(reduce_type)} at {reduce_type.__name__}")

        return DocumentObject(ret)

    def __lshift__(self, other):
        self.__has_set_value__ = True
        data = {}
        if isinstance(other, tuple):
            for x in other:
                if isinstance(x, Field):
                    if not x.__has_set_value__:
                        raise Exception(f"Thous must set {x.__name__}. Example:{x.__name__}<<my_value")
                    data[x.__name__] = x.__value__
                elif isinstance(x, dict):
                    data = {**data, **x}
                else:
                    raise Exception("Invalid expression")
            self.__value__ = data
        else:
            self.__value__ = other
        return self

    def __getattr__(self, item):
        if item[0:2] != "__" and item[-2:] != "__" and self.__check_map__name__ is not None:
            check_name = convention_get(f"{self.__check_map__module__}/{self.__check_map__name__}", item)
            if check_name is None:
                raise AttributeError(f"{item} was not found in {self.__check_map__module__}.{self.__check_map__name__}")
            if isinstance(check_name, dict):
                ret = Field(check_name["__name__"])
                ret.__set_check__(check_name)
                if self.__name__ is not None:
                    ret.__name__ = f"{self.__name__}.{ret.__name__}"
                return ret
            if self.__name__ is None:
                return Field(check_name)
            else:
                return Field(f"{self.__name__}.{check_name}")
        if isinstance(item, str):
            if item[0:2] == "__" and item[-2:] == "__":
                return __BaseField__.__getattr__(self, item)
            elif self.__name__ is None:
                return Field(item)
            else:
                return Field(f"{self.__name__}.{item}")
        else:
            return __BaseField__.__getattr__(self, item)

    def __repr__(self):
        if self.__data__ is not None:
            ret = get_mongodb_text(self.__data__)
            return json.dumps(ret)
        else:
            return self.__name__

    # all compare operator
    def __eq__(self, other):
        op = "$eq"
        if other is None:
            ret= Field(self.__name__)
            ret.__data__={
                "$or":[
                    {
                        self.__name__:{ "$exists": False}
                    },{
                        self.__name__:None
                    }
                ]
            }
            return ret
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: other
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __ne__(self, other):
        op = "$ne"
        if other is None:
            ret= Field(self.__name__)
            ret.__data__={
                "$and":[
                    {
                        self.__name__:{ "$exists": True}
                    },{
                        self.__name__: {"$ne": None}
                    }
                ]
            }
            return ret
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: {
                    "$ne": other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __lt__(self, other):
        op = "$lt"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __le__(self, other):
        op = "$lte"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __gt__(self, other):
        op = "$gt"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __ge__(self, other):
        op = "$gte"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    # all logical
    def __and__(self, other):
        if other is None:
            return self
        if not isinstance(other, Field):
            raise Exception(f"and operation require 2 Field. While {type(other)}")
        return Field(
            {
                "$and": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$and"
        )

    def __or__(self, other):
        if other is None:
            return self
        if not isinstance(other, Field):
            raise Exception(f"and operation require 2 Field")
        return Field(
            {
                "$or": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$or"
        )

    def __invert__(self):
        op = "$not"
        if self.__data__ is not None:
            return Field({
                op: self.to_mongo_db_expr()
            }, op)
        else:
            raise Exception("Invalid expression")

    # all math operator:
    def __add__(self, other):
        if isinstance(other, Field):
            return Field({
                "$add": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$add")
        else:
            return Field({
                "$add": [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, "$add")

    def __sub__(self, other):
        op = "$sub"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)

    def __mul__(self, other):
        op = "$multiply"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)

    def __truediv__(self, other):
        op = "$divide"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)

    def __mod__(self, other):
        op = "$mod"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)

    def __pow__(self, power, modulo=None):
        op = "$pow"
        if isinstance(power, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    power.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    power
                ]
            }, op)

    def __floordiv__(self, other):
        op = "$floor"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)

    # Alias
    def __rshift__(self, other):
        # init_data = self.__field_name__
        init_data = other
        import cy_docs
        if isinstance(other, Field) or isinstance(other, cy_docs.cy_docs_x.Field):
            _expr = other.to_mongo_db_expr()

            if isinstance(_expr, dict):
                expr = {}
                for k, v in _expr.items():
                    if k[0:1] != "$":
                        expr[f"${k}"] = v
                    else:
                        expr[k] = v

                ret = Field(expr)
            else:
                ret = Field(other.__name__)
            ret.__alias__ = self.__name__
            ret.__agg__function_call__ = other.__agg__function_call__

            return ret
        elif type(other) in [int, str, float, bool, datetime.datetime]:
            ret = Field("")
            ret.__name__ = other
            ret.__alias__ = self.__name__

            return ret
        elif isinstance(other, tuple):
            init_data = {}
            for x in other:

                if isinstance(x, Field):
                    init_data[x.__alias__] = x.to_mongo_db_expr()

                else:
                    init_data[f"${x.__name__}"] = 1
            ret = Field(init_data)
            ret.__alias__ = self.__name__
            return ret
        elif isinstance(other, dict):
            ret = Field("")
            ret.__alias__ = self.__name__
            ret.__data__ = other
            ret.__name__ = None
            return ret
        else:
            raise Exception(f"Thous can not alias mongodb expression with {type(other)}")
        return self
    def __contains__(self,other):
        if other is not None and type(other) not in [int,datetime.datetime,bool,str,list,float,dict]:
            raise Exception(f"param in {self.__name__}.__contains__ must be str,int,bool,datetime,float,dict or array")
        ret= Field(self.__name__)
        if isinstance(other,list):
            if any([x for x in other if type(x) not in [int,datetime.datetime,bool,str,list,float,dict]]):
                raise Exception(f"all element in {other} must be str,int,bool,datetime,float,dict or array")
            """
            $all: [{
            "$elemMatch": {
                id: 1234,
                comments: {
                    $in: ['GOOD', 'NICE']
                }
            }
        }, {
            "$elemMatch": {
                id: 2345,
                comments: {
                    $in: ['GOOD']
                }
            }
        }, ]
            """
            all_items= [{"$elemMatch":x} for x in other]
            ret.__data__={
                ret.__name__:{
                    "$all":all_items
                }
            }
            return ret
        elif type(other) in [int,datetime.datetime,bool,list,float,dict]:
            """
            db.survey.find({ results: { $elemMatch: { product: "xyz" } } })
            """
            ret.__data__ = {
                ret.__name__: {
                    "$elemMatch": other
                }
            }
            return ret
        elif isinstance(other,str):
            """
            sub_text = "hello"  # The text you want to check for
                query = {
                    "your_text_field": {
                        "$regex": f"{sub_text}",
                        "$options": "i"  # Enables case-insensitive matching
                    }
                }
            """
            ret.__data__ = {
                ret.__name__: {
                    "$regex": other,
                    "$options": "i"
                }
            }
            return ret




    def asc(self):
        init_data = self.__name__
        if self.__name__ is None:
            init_data = self.__data__
        ret = Field(init_data)
        ret.__sort__ = 1
        return ret

    def like(self, value: str):

        ret = self == re.compile(value, re.IGNORECASE)
        return ret

    def startswith(self, value: str):
        ret = self == re.compile(f"^{value}", re.IGNORECASE)
        return ret

    def endswith(self, value: str):
        ret = self == re.compile(f"{value}^", re.IGNORECASE)
        return ret

    def desc(self):
        init_data = self.__name__
        if self.__name__ is None:
            init_data = self.__data__
        ret = Field(init_data)
        ret.__sort__ = -1
        return ret

    def __to_expr__(self):
        ret_data = {"$expr": self.__data__}
        ret = Field(ret_data)
        return ret

    def __is_type_of__(self, mongodb_type_name: str):

        if self.__name__ is None:
            raise Exception("You can not get type pf expression")
        init_data = {
            self.__name__: {
                "$type": mongodb_type_name
            }
        }
        ret = Field(init_data)
        return ret


__FIELD__ = Field


def to_json_convertable(data, predict_content_handler=None):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = to_json_convertable(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [to_json_convertable(x)]
        return ret
    elif isinstance(data, bson.ObjectId):
        return data.__str__()
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    else:
        return data


class DocumentObject(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def to_json_convertable(self):
        return to_json_convertable(self)

    def get(self, key):

        if isinstance(key, Field):
            items = key.__name__.split('.')
            ret = self
            for x in items:
                ret = dict.get(ret, x)
                if isinstance(ret, dict):
                    ret = DocumentObject(ret)
                if ret is None:
                    return None

            return ret
        else:
            if isinstance(key, str) and key.lower() == "id":
                key = "_id"
            return dict.get(self, key)

    def __getattr__(self, item):
        ret = self.get(item)
        if isinstance(ret, bson.ObjectId):
            return str(ret)
        if isinstance(ret, uuid.UUID):
            return str(ret)
        return ret

    def __setattr__(self, key, value):
        if isinstance(value, dict):
            self[key] = DocumentObject(value)
        else:
            self[key] = value

    def __getitem__(self, key):
        if isinstance(key, Field):
            items = key.__name__.split('.')
            ret = self
            for x in items:
                ret = dict.get(ret, x)
                if isinstance(ret, dict):
                    ret = DocumentObject(ret)
                if ret is None:
                    return None

            return ret
        else:
            if isinstance(key, str) and key.lower() == "id":
                key = "_id"
            return dict.get(self, key)

    def __delitem__(self, key):
        if isinstance(key, Field):
            items = key.__name__.split('.')
            ret = self

            n = len(items) - 1
            for i in range(0, n):
                x = items[i]
                ret = ret[x] or DocumentObject({})
            dict.__delitem__(ret, items[n])

        else:
            if isinstance(key, str) and key.lower() == "id":
                key = "_id"
            dict.__setitem__(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, Field):
            items = key.__name__.split('.')
            ret = self

            n = len(items) - 1
            for i in range(0, n):
                x = items[i]
                ret = ret[x] or DocumentObject({})
            dict.__setitem__(ret, items[n], value)

        else:
            if isinstance(key, str) and key.lower() == "id":
                key = "_id"
            dict.__setitem__(self, key, value)

    def to_pydantic(self) -> pydantic.BaseModel:
        ret = pydantic.BaseModel()
        for k, v in self.to_json_convertable().items():
            ret.__dict__[k] = v
        return ret


class ExprBuilder:
    def __getattr__(self, item):
        return Field(item)

    def __getitem__(self, item):
        if hasattr(item, "__annotations__") and isinstance(item.__annotations__, dict):
            ret = Field(item)
            ret.__set_check__(item)
            return ret
        return Field(item)

    def __set_type__(self, cls: type):
        self.__cls__ = cls


fields = ExprBuilder()


class DBDocument:
    def __init__(self, collection: pymongo.collection.Collection):
        self.collection = collection

    def __lshift__(self, other):
        if isinstance(other, tuple):
            insert_dict = {}
            for x in other:
                if isinstance(x, Field):
                    if not x.__has_set_value__:
                        raise Exception(f"Please set value for {x}")
                    else:
                        insert_dict[x.__name__] = x.__value__
                else:
                    raise Exception("All element in left shift document must be cy_docs.Field. Example:"
                                    "my_doc = cy_docs.get_doc('my-coll-__name__',__client__)"
                                    "test_docs['my-db-__name__']<<( cy_docs.fields.Code <<'001', cy_docs.fields.Name << 'Name'")
            if insert_dict.get("_id") is None:
                insert_dict["_id"] = bson.ObjectId()
            ret = self.collection.insert_one(insert_dict)

            return ret
        else:
            raise Exception("All element in left shift document must be cy_docs.Field. Example:"
                            "my_doc = cy_docs.get_doc('my-coll-__name__',__client__)"
                            "test_docs['my-db-__name__']<<( cy_docs.fields.Code <<'001', cy_docs.fields.Name << 'Name'")

    def __rshift__(self, other):

        if isinstance(other, dict):
            ret = self.collection.find(other)
        elif isinstance(other, Field):
            ret = self.collection.find(other.to_mongo_db_expr())
        else:
            raise Exception("All element in right shift document must be cy_docs.Field. Example:"
                            "my_doc = cy_docs.get_doc('my-coll-__name__',__client__)"
                            "test_docs['my-db-__name__']>>( cy_docs.fields.MyNumber>1000")

        for x in ret:
            if x is None:
                yield None
            yield DocumentObject(x)

    def __matmul__(self, other):
        if isinstance(other, Field):
            ret_item = self.collection.find_one(other.to_mongo_db_expr())
            if ret_item is None:
                return None
            else:

                return DocumentObject(ret_item)
        elif isinstance(other, dict):
            ret_item = self.collection.find_one(other)
            if ret_item is None:
                return None
            else:
                return DocumentObject(ret_item)
        elif type(other) in [int, str, bool, float, datetime.datetime]:
            ret_item = self.collection.find_one({"_id": other})
            if ret_item is None:
                return None
            else:
                return DocumentObject(ret_item)
        else:
            raise Exception("Param in Find one must be cy_docs.Field or dict")

    def delete(self, filter):
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.delete_many(_filter)
        return ret

    async def delete_async(self, filter):
        return self.delete(filter)

    async def find_one_async(self, filter):

        return self.find_one(filter)

    def find_one(self, filter):
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = list(self.collection.find(_filter))
        if len(ret) == 0:
            return None
        return DocumentObject(ret[0])

    async def find_async(self, filter, linmit=10000):

        return self.find(filter=filter, linmit=linmit)

    def find(self, filter, linmit=10000):
        """
        Find documents with filter
        :param filter:
        :param linmit:
        :return:
        """

        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.find(_filter)

        for document in ret:
            yield DocumentObject(document)

    def find_to_json_convertable(self, filter, linmit=10000):

        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.find(_filter)

        for document in ret:
            yield DocumentObject(document).to_json_convertable()

    async def insert_one_async(self, *args, **kwargs):
        return self.insert_one(*args, **kwargs)

    def insert_one(self, *args, **kwargs):
        if isinstance(args, Field):
            ret = self.collection.insert_one({
                args.__name__: args.__value__
            })
            return ret
        if isinstance(args, tuple):
            if len(args) == 1:
                if isinstance(args[0], dict):
                    for k, v in kwargs:
                        args[0][k] = v
                    if args[0].get("_id") is None:
                        args[0] = bson.ObjectId()
                    ret = self.collection.insert_one(args[0])
                    return ret
                elif isinstance(args[0], Field):
                    _fx: Field = args[0]
                    if not _fx.__has_set_value__:
                        raise Exception(
                            f"Please set value for {_fx.__name__}. Example: {_fx.__name__}<<my_value")
                    data = {
                        _fx.__name__: _fx.__value__
                    }
                    for k, v in kwargs:
                        data[k] = v
                    if data.get("_id") is None:
                        data["_id"] = bson.ObjectId()
                    ret = self.collection.insert_one(data)
                    return ret
            else:
                data = {}
                for x in args:
                    if isinstance(x, Field):
                        if not x.__has_set_value__:
                            raise Exception(
                                f"Please set value for {x.__name__}. Exmaple {x.__name__}<<my_value")
                        data[x.__name__] = x.__value__
                    elif isinstance(x, dict):
                        data = {**data, **x}
                if data.get("_id") is None:
                    data["_id"] = bson.ObjectId()
                ret = self.collection.insert_one(data)
                return ret

    def count(self, filter):
        if isinstance(filter, dict):
            return self.collection.count_documents(filter)
        elif isinstance(filter, Field):
            return self.collection.count_documents(filter.to_mongo_db_expr())

    def update(self, filter, *args, **kwargs):
        _filter = {}
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()
        updater = {}
        for x in args:
            if isinstance(x, Field):
                if not x.__has_set_value__:
                    raise Exception(f"Thous must set {x.__name__} a value. Exmaple: {x.__name__}<<my_value")
                updater[x.__name__] = x.__value__
            elif isinstance(x, dict):
                updater = {**updater, **x}
        updater = {**updater, **kwargs}
        _inc_ = {}
        _set_ = {}

        for k, v in updater.items():
            if k == "$inc":
                _inc_[k] = v
            else:
                _set_[k] = v
        _update_ = {

        }

        if len(_set_.keys()) > 0:
            _update_["$set"] = _set_
        if len(_inc_.keys()) > 0:
            _update_ = {**_update_, **_inc_}
        ret = self.collection.update_many(
            filter=_filter,
            update=_update_
        )
        return ret

    async def update_async(self, filter, *args, **kwargs):
        return self.update(filter, *args, **kwargs)

    async def count_async(self, filter):
        return self.count(filter)

    def aggregate(self):
        return AggregateDocument(self)


class AggregateDocument:
    def __init__(self, owner: DBDocument):
        self.owner = owner
        self.pipeline = []

    def project(self, *args, **kwargs):
        """
        Exmaple:
        project(
            mydocument.Name,
            cy_docs.fields.code>> mydocument.Code,
            ....,
            cy_docs.fields.day >> mydocument.Mydate.dayOfMonth()
        )
        or
        project(
            {   "name":1,
                "code":"$Code",
                "day":{"$dayOfMonth":"$Mydate"}
            }
        )
        :param args:
        :param kwargs:
        :return:
        """
        import cy_docs
        stage = {

        }
        if isinstance(args, Field):
            if args.__agg__function_call__:
                return self.group(args)
            if args.__alias__ is not None:
                stage[args.__alias__] = args.to_mongo_db_expr()
            elif args.__name__ is not None:
                stage[args.__name__] = 1
            else:
                raise Exception(f"Thous can not use project stage with {args}")
        elif isinstance(args, tuple) or isinstance(args, list):
            agg_fields = [x for x in args if
                          (isinstance(x, Field) or isinstance(x, cy_docs.cy_docs_x.Field)) and x.__agg__function_call__]
            if len(agg_fields) > 0:
                return self.group(*args)
            else:
                import cy_docs

                for x in args:
                    if isinstance(x, Field) or isinstance(x, cy_docs.cy_docs_x.Field):
                        if x.__alias__ is not None:
                            stage[x.__alias__] = x.to_mongo_db_expr()
                        elif x.__name__ is not None:
                            stage[x.__name__] = 1
                        else:
                            raise Exception(f"Thous can not use project stage with {x}")
                    elif isinstance(x, dict):
                        stage = {**stage, **x}
                    elif isinstance(x, str):
                        stage[x] = 1
                    else:
                        raise Exception(f"Thous can not use project stage with {x}")

                stage = {**stage, **kwargs}
        if stage.get("_id") is None:
            stage["_id"] = 0

        self.pipeline += [
            {
                "$project": stage
            }
        ]

        return self

    def match(self, filter):
        if isinstance(filter, dict):
            self.pipeline += [
                {
                    "$match": filter
                }
            ]
        elif isinstance(filter, Field):
            self.pipeline += [
                {
                    "$match": filter.to_mongo_db_expr()
                }
            ]
        return self

    def sort(self, *args, **kwargs):
        stage = {

        }
        if isinstance(args, Field):
            if args.__alias__ is not None:
                stage[args.__alias__] = args.to_mongo_db_expr()
            elif args.__name__ is not None:
                stage[args.__name__] = args.__sort__
            else:
                raise Exception(f"Thous can not sort stage with {args}")
        for x in args:
            if isinstance(x, Field):
                if x.__alias__ is not None:
                    raise Exception(f"Thous can not sort stage with {x}")
                elif x.__name__ is not None:
                    stage[x.__name__] = x.__sort__
                else:
                    raise Exception(f"Thous can not sort stage with {x}")

            else:
                raise Exception(f"Thous can not use sort stage with {x}")

        stage = {**stage, **kwargs}

        self.pipeline += [
            {
                "$sort": stage
            }
        ]

        return self

    def skip(self, len: int):
        self.pipeline += [
            {
                "$skip": len
            }
        ]
        return self

    def limit(self, len: int):
        self.pipeline += [
            {
                "$limit": len
            }
        ]
        return self

    def __inspect__(self, field):
        assert isinstance(field, Field)
        if field.__agg__function_call__:
            return None, field
        else:
            return field, None

    def group(self, *selector):
        if isinstance(selector, dict):
            select_fields = list((selector.get('_id') | {}).keys())
            select_fields += list(selector.keys())
            select_fields = list(set(select_fields))
            project_pipe = {}
            for x in select_fields:
                project_pipe[x] = f"${x.lstrip('$')}"
            self.pipeline += [
                {
                    "$group": selector
                },
                {
                    "$project": project_pipe
                }
            ]
        if isinstance(selector, Field):
            _id, _field = self.__inspect__(selector)
            return self.__group__(_id, _field)
        elif isinstance(selector, tuple):
            _ids, _fields = [], []
            for x in selector:
                assert isinstance(x, Field)
                _id, _field = self.__inspect__(x)
                if _id:
                    _ids += [_id]
                if _field:
                    _fields += [_field]
            return self.__group__(
                group_by=tuple(_ids),
                accumulators=tuple(_fields)
            )

    def __group__(self, group_by, accumulators):
        _id = {}
        _fields = {}
        _ignore_ = {}
        if isinstance(group_by, dict):
            _id = group_by
        elif isinstance(group_by, tuple) or isinstance(group_by, list):
            for x in group_by:
                if isinstance(x, dict):
                    _id = {**_id, **x}
                elif isinstance(x, Field):
                    if isinstance(x.__data__, dict) and x.__alias__:
                        _id = {**_id, **{x.__alias__: x.__data__}}
                    elif x.__name__:
                        _id = {**_id, **{x.__name__: f"${x.__name__}"}}
                    else:
                        raise Exception("Invalid expression")

        if isinstance(accumulators, dict):
            _fields = accumulators
        elif isinstance(accumulators, Field):
            if isinstance(accumulators.__data__, dict):
                if accumulators.__agg__function_call__:
                    _ignore_[list(accumulators.__data__.keys())[0].lstrip('$') + "_count"] = 1
                    _id = {**_id,
                           **{list(accumulators.__data__.keys())[0].lstrip('$') + "_count":
                                  list(accumulators.__data__.keys())[0]}}
                    _fields = {**_fields, **{accumulators.__alias__: {
                        "$sum": 1
                    }}}
                if accumulators.__alias__:
                    _fields = {**_fields, **{accumulators.__alias__: accumulators.__data__}}
                else:
                    _fields = {**_fields, **accumulators.__data__}
            else:
                _fields = {**_fields, **{accumulators.__name__: f"${accumulators.__name__}"}}
        elif isinstance(accumulators, tuple) or isinstance(accumulators, list):
            for x in accumulators:
                if isinstance(x, dict):
                    _fields = {**_fields, **x}
                elif isinstance(x, Field):
                    if isinstance(x.__data__, dict):
                        if x.__agg__function_call__ == "$count" and x.__alias__:
                            _ignore_[list(x.__data__.keys())[0].lstrip('$') + "_count"] = 1
                            _id = {**_id,
                                   **{list(x.__data__.keys())[0].lstrip('$') + "_count": list(x.__data__.keys())[0]}}
                            _fields = {**_fields, **{x.__alias__: {
                                "$sum": 1
                            }}}

                        elif x.__alias__:
                            _fields = {**_fields, **{x.__alias__: x.__data__}}
                        else:
                            _fields = {**_fields, **x.__data__}
                    else:
                        _fields = {**_fields, **{x.__name__: f"${x.__name__}"}}
        _group_ = {**{"_id": _id}, **_fields}
        _project_ = {"_id": 0}
        for k, v in _id.items():
            if _ignore_.get(k) is None:
                _project_[k] = f"$_id.{k}"
        for k, v in _fields.items():
            if _ignore_.get(k) is None:
                _project_[k] = f"${k}"
        self.pipeline += [
            {
                "$group": _group_
            }, {
                "$project": _project_
            }
        ]
        return self

    def __repr__(self):
        ret_pipe = ""
        for x in self.pipeline:
            b = to_json_convertable(x)
            ret_pipe += json.dumps(b) + ",\n"
        ret_pipe = ret_pipe[:-1]
        ret = f"db.getCollection('{self.owner.collection.name}').aggregate([\n{ret_pipe}\n])"
        return ret

    def __iter__(self):
        ret = self.owner.collection.aggregate(
            self.pipeline
        )
        for x in ret:
            yield DocumentObject(x)

    def to_json_convertable(self):
        for x in self:
            yield to_json_convertable(x)

    def first_item(self):
        items = list(self)
        if len(items) == 0:
            return None
        else:
            return DocumentObject(items[0])


__cache_index__ = dict()
__cache_unique__ = dict()
__lock__ = threading.Lock()


class Document:
    def __init__(self, collection_name: str, client: pymongo.mongo_client.MongoClient, indexes=[], unique_keys=[]):
        self.client = client
        self.collection_name = collection_name
        self.indexes = indexes
        self.unique_keys = unique_keys
        self.__majority_concern__ = None

    def set_majority_concern(self):
        self.__majority_concern__ = True

    def __getitem__(self, item):
        from pymongo.read_concern import ReadConcern
        from pymongo.write_concern import WriteConcern
        from pymongo.read_preferences import ReadPreference

        global __cache_index__
        global __cache_unique__
        global __lock__
        if self.__majority_concern__:
            coll = self.client.get_database(item).get_collection(
                self.collection_name
                # read_concern=ReadConcern('majority'),
                # write_concern=WriteConcern('majority'),
                # read_preference=ReadPreference.PRIMARY
            )
        else:
            coll = self.client.get_database(item).get_collection(
                self.collection_name
            )

        def run_create_index():
            for x in self.unique_keys:
                key = f"{item}.{self.collection_name}.{x}"
                if __cache_unique__.get(key) is None:
                    # __lock__.acquire()
                    try:
                        fx = coll.index_information()
                        indexes = []
                        for y in x.split(','):
                            if fx.get(f"{x}_1") is None:
                                indexes.append(
                                    (y, pymongo.ASCENDING)
                                )
                        if len(indexes) > 0:
                            coll.create_index(
                                indexes,
                                background=True,
                                unique=True,
                                sparse=True,
                            )
                    except Exception as e:
                        pass
                    finally:
                        # __lock__.release()
                        __cache_unique__[key] = key
            for x in self.indexes:
                key = f"{item}.{self.collection_name}.{x}"
                if __cache_index__.get(key) is None:
                    # __lock__.acquire()
                    try:
                        indexes = []
                        for y in x.split(','):
                            indexes.append(
                                (y, pymongo.ASCENDING)
                            )
                        coll.create_index(
                            indexes,
                            background=True
                        )
                    except Exception as e:
                        pass
                    finally:
                        # __lock__.release()
                        __cache_index__[key] = key

        thread = threading.Thread(target=run_create_index)

        # Set the daemon property to True
        thread.daemon = True

        # Start the thread
        thread.start()

        return DBDocument(coll)


def get_doc(collection_name: str, client: pymongo.mongo_client.MongoClient, indexes: List[str] = [],
            unique_keys: List[str] = []) -> Document:
    return Document(collection_name, client, indexes=indexes, unique_keys=unique_keys)


class Funcs:
    @staticmethod
    def concat(*args):
        data = {}
        __args = []
        for x in args:
            if isinstance(x, Field):
                __args += [x.to_mongo_db_expr()]
            elif hasattr(x, "__str__"):
                __args += [x.__str__()]
            else:
                __args += [f"{x}"]
        data = {
            "$concat": __args
        }
        return Field(data, "$concat")

    @staticmethod
    def exists(field):
        if isinstance(field, Field):
            return Field({
                field.__name__: {
                    "$exists": True
                }
            })
        elif isinstance(field, str):
            return Field({
                field: {
                    "$exists": True
                }
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-__name__> or str")

    @staticmethod
    def is_null(field):
        if isinstance(field, Field):
            return Field({
                field.__name__: None
            })
        elif isinstance(field, str):
            return Field({
                field: None
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-__name__> or str")

    @staticmethod
    def is_not_null(field):
        if isinstance(field, Field):
            return Field({
                field.__name__: {"$ne:": None}
            })
        elif isinstance(field, str):
            return Field({
                field: {"$ne:": None}
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-__name__> or str")

    @staticmethod
    def not_exists(field):
        if isinstance(field, Field):
            return Field({
                field.__name__: {
                    "$exists": False
                }
            })
        elif isinstance(field, str):
            return Field({
                field: {
                    "$exists": False
                }
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-__name__> or str")


__DbContext__cache__ = {}
__DbContext__cache__lock__ = threading.Lock()


class DbContext(object):
    def __new__(cls, *args, **kw):
        global __DbContext__cache__
        global __DbContext__cache__lock__
        if not hasattr(cls, '_instance'):
            __DbContext__cache__lock__.acquire()
            try:
                orig = super(DbContext, cls)
                cls._instance = orig.__new__(cls)
                cls._instance.__init__(*args, **kw)

                def empty(obj, *a, **b):
                    pass

                setattr(cls, "__init__", empty)
            except Exception as e:
                raise e
            finally:
                __DbContext__cache__lock__.release()
        return cls._instance


def document_define(name: str, indexes: List[str], unique_keys: List[str]):
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
    :param unique_keys:
    :return:
    """

    def wrapper(cls):
        setattr(cls, "__document_name__", name)
        setattr(cls, "__document_indexes__", indexes)
        setattr(cls, "__document_unique_keys__", unique_keys)

        return cls

    return wrapper


def context(client, cls, majority=False):
    ret = Document(
        collection_name=cls.__document_name__,
        indexes=cls.__document_indexes__,
        unique_keys=cls.__document_unique_keys__,
        client=client
    )
    if majority:
        ret.set_majority_concern()
    return ret


def file_get(client, db_name: str, file_id):
    gfs = gridfs.GridFSBucket(client.get_database(db_name), chunk_size_bytes=1024 * 1024 * 2)

    if isinstance(file_id, str):
        file_id = bson.ObjectId(file_id)

    ret = gfs.open_download_stream(file_id)

    # ret = gridfs.GridFS(__client__.get_database(__db_name__)).get(file_id)
    return ret


async def file_get_async(client, db_name: str, file_id):
    return file_get(client, db_name, file_id)


def file_get_by_name(client, db_name: str, filename):
    gfs = gridfs.GridFSBucket(client.get_database(db_name))
    items = list(gfs.find({"filename": filename}))
    if len(items) > 0:
        return items[0]


async def file_get_by_name(client, db_name: str, filename):
    return file_get_by_name(client, db_name, filename)


@document_define(
    name="fs.files",
    unique_keys=["rel_file_path"],
    indexes=[]

)
class __fs_files__:
    _id: bson.ObjectId
    chunkSize: int
    length: int
    rel_file_path: str
    filename: str
    currentChunkIndex: int


@document_define(
    name="fs.chunks",
    indexes=["files_id", "files_id,n", "n", "_id,files_id,n"],
    unique_keys=[]
)
class __fs_files_chunks__:
    _id: bson.ObjectId
    files_id: bson.ObjectId
    n: int
    data: bytes


def file_chunk_count(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId) -> int:
    if isinstance(file_id, str):
        file_id = bson.ObjectId(file_id)
    ret = context(client, __fs_files_chunks__)[db_name].count(
        {
            "files_id": file_id
        }
    )

    return ret


def file_add_chunk(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId, chunk_index: int,
                   chunk_data: bytes):
    if isinstance(file_id, str):
        file_id = bson.ObjectId(file_id)
    context(client, __fs_files_chunks__)[db_name].insert_one(
        {
            "_id": bson.objectid.ObjectId(),
            "files_id": file_id,
            "n": chunk_index,
            "data": chunk_data
        }
    )

    del chunk_data


from pymongo import InsertOne, ReadPreference
import pymongo.errors


def file_add_chunks(client: pymongo.MongoClient, db_name: str, file_id: bson.ObjectId, data: bytes,
                    index_chunk: int = 0):
    files_context = context(client, __fs_files__, majority=True)[db_name]

    fs = files_context.find_one(
        {
            "_id": file_id
        }
    )
    if fs is None:
        raise pymongo.errors.CursorNotFound("File was not found")
    # db_context = context(client, __fs_files_chunks__)[db_name]
    num_of_chunks, m = divmod(len(data), fs.chunkSize)
    if m > 0: num_of_chunks += 1
    if index_chunk > 0:
        index_chunk = index_chunk * num_of_chunks
    start_chunk_index = fs.get("currentChunkIndex") or 0
    files_context.update(
        fields._id == file_id,
        fields.currentChunkIndex << (start_chunk_index + num_of_chunks)
    )

    remain = len(data)
    start = 0
    requests = []
    bulk_collection = client.get_database(db_name).get_collection("fs.chunks")
    t = datetime.datetime.utcnow()
    for i in range(0, num_of_chunks):
        end = start + min(fs.chunkSize, remain)
        remain = remain - fs.chunkSize
        chunk_data = data[start:end]
        start = end

        requests += [InsertOne(
            {
                "_id": bson.objectid.ObjectId(),
                "files_id": file_id,
                "n": start_chunk_index + i,
                "data": chunk_data
            }
        )]

    ret = bulk_collection.bulk_write(
        requests=requests,
        ordered=True,
        bypass_document_validation=True
    )


def file_get_iter_contents(client, db_name, files_id, from_chunk_index_index, num_of_chunks):
    collection = client.get_database(db_name).get_collection("fs.chunks")
    ret = collection.find({
        "files_id": files_id,
        "n": {
            "$gte": from_chunk_index_index,

        }
    },

        limit=num_of_chunks
    ).sort("n", pymongo.ASCENDING)

    return ret


def create_file(client, db_name: str, file_name: str, content_type: str, file_size, chunk_size):
    gfs = gridfs.GridFS(client.get_database(db_name))  # gridfs.GridFSBucket(__client__.get_database(__db_name__))

    fs = gfs.new_file()
    fs.name = file_name
    fs.filename = file_name
    fs.close()
    num_of_chunks, m = divmod(file_size, chunk_size)
    if m > 0: num_of_chunks += 1

    context(client, __fs_files__)[db_name].update(
        fields._id == fs._id,
        fields.chunkSize << chunk_size,
        fields.length << file_size,
        fields.rel_file_path << file_name,
        fields.contentType << content_type,
        fields.numOfChunks << num_of_chunks
    )
    ret = gfs.get(fs._id)
    return ret


def get_file_info_by_id(client, db_name, files_id):
    if isinstance(files_id, str):
        files_id = bson.ObjectId(files_id)
    ret = context(client, __fs_files__)[db_name].find_one(
        fields._id == files_id
    )
    return ret


# async def get_file_async(client, db_name: str, file_id):
#
#     async_client = AsyncIOMotorClient()
#     async_client.delegate = client
#     gfs = AsyncIOMotorGridFSBucket(async_client.get_database(db_name))
#
#     if isinstance(file_id, str):
#         file_id = bson.ObjectId(file_id)
#     ret = await gfs.open_download_stream(file_id)
#     # ret = gridfs.GridFS(__client__.get_database(__db_name__)).get(file_id)
#     return ret


# async def find_file_async(client, db_name: str, rel_file_path: str):
#     from motor.motor_asyncio import AsyncIOMotorClient
#     async_client = AsyncIOMotorClient()
#     async_client.delegate = client
#     gfs = AsyncIOMotorGridFSBucket(async_client.get_database(db_name))
#     ret = await  gfs.find({"rel_file_path": rel_file_path})
#
#     # ret = gridfs.GridFS(__client__.get_database(__db_name__)).get(file_id)
#     return ret


def EXPR(expr):
    if isinstance(expr, dict):
        ret = Field()
        ret.__data__ = {
            "$expr": expr
        }
        return ret
    elif isinstance(expr, Field):
        ret = Field()
        ret.__data__ = {
            "$expr": expr.to_mongo_db_expr()
        }
        return ret


class FUNCS:

    @classmethod
    def cond(cls, check, then_case, else_case):
        _cond_ = {}
        if isinstance(check, Field):
            _cond_["if"] = check.to_mongo_db_expr()
        else:
            _cond_["if"] = check
        if isinstance(then_case, Field):
            _cond_["then"] = then_case.to_mongo_db_expr()
        else:
            _cond_["then"] = then_case
        if isinstance(else_case, Field):
            _cond_["else"] = else_case.to_mongo_db_expr()
        else:
            _cond_["else"] = else_case
        ret_field = Field(init_value={
            "$cond": _cond_
        })
        return ret_field

    @staticmethod
    def count(field: typing.Optional[typing.Union[Field, str]] = None):
        return FUNCS.__agg_func_call_("$count", field)

    @staticmethod
    def sum(field: typing.Union[Field, str]):
        return FUNCS.__agg_func_call_("$sum", field)

    @staticmethod
    def min(field: typing.Union[Field, str]):
        return FUNCS.__agg_func_call_("$min", field)

    @staticmethod
    def max(field: typing.Union[Field, str]):
        return FUNCS.__agg_func_call_("$max", field)

    @classmethod
    def first(cls, field: typing.Union[Field, str]):
        return FUNCS.__agg_func_call_("$first", field)

    @classmethod
    def last(cls, field: typing.Union[Field, str]):
        return FUNCS.__agg_func_call_("$last", field)

    @staticmethod
    def __agg_func_call_(function_name: str, field):
        if isinstance(field, str):
            ret = Field(init_value="_")
            ret.__name__ = None
            ret.__data__ = {
                function_name: f"${field}"
            }
            ret.__agg__function_call__ = function_name
            return ret
        elif isinstance(field, Field):
            if field.__name__ and field.__data__ is None:
                ret = Field(init_value="_")
                ret.__name__ = None
                ret.__data__ = {
                    function_name: f"${field.__name__}"
                }
                ret.__agg__function_call__ = function_name
                return ret
            elif isinstance(field.__data__, dict):
                ret = Field(init_value="_")
                ret.__name__ = None
                ret.__data__ = {
                    function_name: field.__data__
                }
                ret.__agg__function_call__ = function_name
                return ret
            else:
                raise Exception(f"{field} is invalid")

        raise Exception(f"{field} is invalid")


from typing import Generic, TypeVar

T = TypeVar('T')


class QueryableCollection(Generic[T]):
    def __init__(self, cls, client: pymongo.MongoClient, db_name: str):
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
        return fields[self.__cls__]


def queryable_doc(
        client: pymongo.MongoClient,
        db_name: str, instance_tye: T,
        document_name: str = None) -> \
        QueryableCollection[T]:
    if document_name is None and not hasattr(instance_tye, "__document_name__"):
        raise Exception(f"{instance_tye} was not 'cy_docs.define'")
    if isinstance(document_name, str) and not hasattr(instance_tye, "__document_name__"):
        ret_type = document_define(name=document_name)(instance_tye)
        return QueryableCollection[T](ret_type, client, db_name)
    return QueryableCollection[T](instance_tye, client, db_name)
