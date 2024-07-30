import typing

from mongoengine import (
    Document,EmbeddedDocument,
    StringField,
    IntField,
    DateTimeField,
    BooleanField,
    FloatField,
    DynamicField, ObjectIdField, ListField, EmbeddedDocumentField

)
from mongoengine.base import ComplexBaseField, BaseField, BaseDict

import datetime, types
import bson.objectid
from pymongo.mongo_client import MongoClient


def __extract_annotations__(doc_annotations: dict) -> dict:
    fields = {}
    for k, v in doc_annotations.items():
        if hasattr(v, "_name"):
            t_name = v._name
            if t_name == "Optional":
                t_type = v.__args__[0]
                if hasattr(t_type, "_name"):
                    t_sub_name = t_type._name
                    t_sub_type = t_type.__args__[0]
                    if t_sub_name == 'List':
                        if issubclass(t_sub_type, dict):
                            fields[k] = ListField(DynamicField(), required=False)
                            continue
                        elif t_sub_type == str:
                            fields[k] = ListField(StringField, required=False)
                            continue
                        else:
                            raise NotImplementedError(
                                f"{t_name}/{t_sub_name} and {t_type}/{t_sub_type} was not implemented")
                    raise NotImplementedError(f"{t_name} and sub {t_type} was not implemented")
                else:
                    if t_type == str:
                        fields[k] = StringField(required=False)
                        continue
                    elif t_type == int:
                        fields[k] = IntField(required=False)
                        continue
                    elif t_type == bool:
                        fields[k] = BooleanField(required=False)
                        continue
                    elif issubclass(t_type, dict):
                        fields[k] = DynamicField(required=False)
                        continue
                    elif t_type == bson.objectid.ObjectId:
                        fields[k] = ObjectIdField(required=False)
                        continue
                    elif issubclass(t_type, datetime.datetime):
                        fields[k] = DateTimeField(required=False)
                        continue
                    elif hasattr(t_type, "__annotations__"):
                        fields[k] = __extract_annotations__(t_type.__annotations__)
                        continue
                    else:
                        raise NotImplementedError(f"{t_name} and {t_type} was not implemented")


        elif issubclass(type(v), types.UnionType):
            fields[k] = DynamicField(required=False)
            continue
        else:
            if issubclass(v, str):
                fields[k] = StringField(required=True)
            elif issubclass(v, datetime.datetime):
                fields[k] = DateTimeField(required=True)
            elif issubclass(v, int):
                fields[k] = IntField(required=True)
            elif issubclass(v, bool):
                fields[k] = IntField(required=True)
            elif issubclass(v, float):
                fields[k] = FloatField(required=True)
            elif issubclass(v, bson.ObjectId):
                fields[k] = ObjectIdField(required=True)
            elif issubclass(v, dict):
                fields[k] = DynamicField(required=True)
            elif hasattr(v, "__annotations__"):
                fields[k] = __extract_annotations__(v.__annotations__)
            else:
                raise NotImplementedError(f"{v} is not instance")

    return fields


import functools


@functools.cache
def __extract_annotations_from_class__(cls) -> dict:
    if hasattr(cls, "__annotations__") and isinstance(cls.__annotations__, dict):
        return __extract_annotations__(cls.__annotations__)
    else:
        raise Exception(f"{cls} do not have __annotations__")


def __create_coll_from_dict__(
        fields: dict,
        col_name: str | None = None,
        unique_index = None,
        index= None,
        search_index= None,
        is_embedded_document=False):

    ReClass = None
    if not is_embedded_document:
        class _ReClass(Document):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._data = kwargs

        ReClass = _ReClass
    else:
        class _ReClass(EmbeddedDocument):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._data = kwargs

        ReClass = _ReClass

    setattr(ReClass, "_fields", {})
    setattr(ReClass, "_fields_ordered", [])
    index_specs = []
    for x in unique_index or []:
        unique_data = dict(
            fields=x.split(','),
            unique=True,
            sparse=True
        )
        index_specs += [unique_data]
    for x in index or []:
        unique_data = dict(
            fields=x.split(',')
        )
        index_specs += [unique_data]
    _meta = dict(
        index_background=True,
        auto_create_index=True,
        index_specs = index_specs,
        ordering="_id"
    )
    if col_name:
        _meta['collection'] = col_name
        # setattr(ReClass, "_meta", {'collection': col_name})
    for k, v in fields.items():
        ReClass._fields_ordered += [k]
        if isinstance(v, dict):
            sub_class = __create_coll_from_dict__(v,is_embedded_document=True)
            setattr(ReClass,k,sub_class)
            ReClass._fields[k] = EmbeddedDocumentField(sub_class)
            setattr(ReClass._fields[k], "name", k)
            setattr(ReClass._fields[k], "db_field", k)
        elif isinstance(v, BaseField):
            ReClass._fields[k] = v
            setattr(ReClass._fields[k], "name", k)
            setattr(ReClass._fields[k], "db_field", k)
        else:
            raise Exception(f"{v} do not implemented")
    if not 'id' in ReClass._fields_ordered:
        ReClass._fields_ordered += ['_id']
        ReClass._fields["_id"] = ObjectIdField()
        _meta["id_field"] = "_id"
    setattr(ReClass, "_meta", _meta)
    ReClass._fields_ordered = tuple(ReClass._fields_ordered)

    return ReClass


@functools.cache
def get_coll(cls) -> typing.Type[Document]:
    if not hasattr(cls, "__document_name__"):
        raise Exception(f"{cls} must be wrapppr with cy_docs.define")
    doc_name = cls.__document_name__
    doc_index = cls.__document_indexes__
    doc_unique_index = cls.__document_unique_keys__
    doc_search_fields = cls.__document_search_fields__
    fields = __extract_annotations__(cls.__annotations__)
    ret = __create_coll_from_dict__(
        fields=fields,
        col_name=doc_name,
        unique_index=doc_unique_index,
        index=doc_index,
        search_index=doc_search_fields

    )
    return ret
