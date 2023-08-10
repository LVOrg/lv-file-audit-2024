import json

from elasticsearch import Elasticsearch
from typing import List

client = Elasticsearch(
    hosts="192.168.18.36:9200",
)


def get_all_index(client: Elasticsearch) -> List[str]:
    return list(client.indices.get_alias("*").keys())


class BaseDoc:
    def __init__(self, name: str = None):
        self.name = name
        self.es_expr = None
        self.is_bool = False
        # self.is_equal = False

    def __getattr__(self, item):
        if self.name is not None:
            return BaseDoc(f"{self.name}.{item}")
        return BaseDoc(item)

    def __eq__(self, other):
        ret = BaseDoc()
        self.is_bool = True
        ret.es_expr = {
            "term": {
                f"{self.name}":other
            }
        }
        return ret

    def __or__(self, other):
        ret = BaseDoc()
        if isinstance(other, BaseDoc):
            left = self.es_expr
            if left.get("term"):
                left["match"]= left["term"]
                del left["term"]
            rigt = other.es_expr
            if rigt.get("term"):
                rigt["match"] = rigt["term"]
                del rigt["term"]
            ret.es_expr = {
                "should": [
                    left,rigt
                ]
            }
            ret.is_bool = True
            return ret
        else:
            raise Exception("invalid expr")
    def __and__(self, other):
        ret = BaseDoc()
        if isinstance(other, BaseDoc):
            left = self.es_expr
            if left.get("match"):
                left["term"] = left["match"]
                del left["match"]

            rigt = other.es_expr
            if rigt.get("match"):
                rigt["term"] = rigt["match"]
                del rigt["match"]
            ret.es_expr = {
                "should": [
                    left, rigt
                ]
            }
            ret.is_bool = True
            return ret

        else:
            raise Exception("invalid expr")

    def boost(self, value: float):
        if isinstance(self.es_expr, dict):
            self.es_expr["boost"] = value
        return self

    def __repr__(self):
        if isinstance(self.es_expr, dict):
            return json.dumps(self.get_expr())
        return self.name

    def get_expr(self):
        if isinstance(self.es_expr, dict):
            ret = self.es_expr
            if self.name is not None:
                return {
                    "term":{
                        self.name:{
                            "value":self.es_expr
                        }
                    }
                }
            if self.is_bool:
                ret = {
                    "bool": ret
                }
            return dict(query=ret)
        return self.name


def search(client: Elasticsearch, index: str, filter):
    if isinstance(filter, dict):
        return client.search(index=index, doc_type="doc", body=dict(
            query=filter,
            sort='_score,price'
        ))
    elif isinstance(filter, BaseDoc):
        return client.search(index=index, doc_type="_doc", body=filter.get_expr())


docs = BaseDoc()
