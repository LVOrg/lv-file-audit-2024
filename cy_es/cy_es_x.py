import datetime
import inspect
import json
import os
import time
import typing
import uuid

import elasticsearch.exceptions
from elasticsearch import Elasticsearch
from typing import List
import pydantic
from enum import Enum
import os


def get_info(client: Elasticsearch):
    return client.info()


def get_version(client: Elasticsearch):
    ret = get_info(client)
    __version__ = ret.get('version').get('number').spit('.')
    return __version__


def version() -> str:
    return f"0.0.9{os.path.splitext(__file__)[1]}"


def get_all_index(client: Elasticsearch) -> List[str]:
    return list(client.indices.get_alias("*").keys())


def __well_form__(item):
    r = ["'", '"', ";", ":", ".", ",", ">", "<", "?", "+", "-", "/", "%", "$", "#", "@", "\\", "!", "~",
         "`", "^", "]", "[", "(", ")"]
    ret = ""
    for x in item:
        if x in r:
            ret += f"\\{x}"
        else:
            ret += f"{x}"

    return ret


def __make_up_es_syntax_depriciate__(field_name: str, value):
    if '.' not in field_name:
        return {"term": {field_name: value}}
    else:
        path = ""
        items = field_name.split('.')
        for i in range(0, len(items) - 1):
            path += items[i] + "."
        path = path[:-1]
        return {
            "nested": {
                "path": items[0],
                "query": {
                    "term": {field_name: value}
                }
            }
        }


def __make_up_es_syntax__(field_name: str, value, is_match=False):
    assert isinstance(field_name, str)
    if type(value) == list:
        """
        "terms_set": {
      "programming_languages": {
        "terms": [ "c++", "java", "php" ],
        "minimum_should_match_field": "required_matches"
      }
    }
        """
        return {
            "terms_set": {
                field_name: {
                    "terms": value,
                    "minimum_should_match_script": {
                        "source": f"Math.min(params.num_terms, {len(value)})"
                    },
                }
            }

        }
    """
     return {
                    "terms":  {field_name: value},
                    "minimum_should _match": value.__len__()
                }
    """
    __key__ = "match" if is_match else "term"
    return {__key__: {field_name: value}}


def __make_up_es1__(field_name: str, value):
    items = field_name.split('.')
    if len(items) == 1: return {field_name: value}
    ptr = {}
    ret = ptr

    n = len(items)
    for i in range(0, n):
        index = n - i - 1
        ptr[items[index]] = {}
        ptr = ptr[items[index]]
    ptr[items[n - 1]] = {"value": value}
    return ret


def __check_is_painless_expr__(__es_expr__):
    return isinstance(__es_expr__, dict) and __es_expr__.get("script") and __es_expr__["script"].get(
        "script") and __es_expr__["script"]["script"].get("source")


class DocumentFields:
    """
    ElasticcSearch document gearing \n
    Help Developer build ElasticSearch filter with real Python code
    Example:
        filter = (DocumentFields("my_doc")!=None) & (DocumentFields("my_doc").Code=="XYZ")
        will generate
        {
                 "query": {
                  "bool": {
                   "must": [
                    {
                     "bool": {
                      "must": {
                       "exists": {
                        "field": "MyDoc"
                       }
                      }
                     }
                    },
                    {
                     "term": {
                      "MyDoc.Code": "xyz"
                     }
                    }
                   ]
                  }
                 }
    """

    def __init__(self, name: str = None,is_bool=False):
        self.__name__ = name
        self.__es_expr__ = None
        self.__is_bool__ = is_bool
        self.__value__ = None
        self.__has_set_value__ = None
        self.__minimum_number_should_match__ = None
        self.__norm__ = None
        self.__type__ = None
        self.__wrap_func__ = None
        self.__highlight_fields__ = []
        # self.is_equal = False

    def get_highlight_fields(self):
        ret = []
        for x in self.__highlight_fields__:
            ret += [DocumentFields(x)]
        return ret

    def set_type(self, str_type: str):
        self.__type__ = str_type
        return self

    def set_norms(self, enable: bool):
        """

        :param enable:
        :return:
        """
        """
        "properties": {
    "title": {
      "type": "text",
      "norms": false
    }
  }
        """
        self.__norm__ = enable
        return self

    def get_mapping(self):
        return {
            self.__name__:
                dict(

                    type=self.__type__,
                    norms=self.__norm__
                )
        }

    def set_minimum_should_match(self, value):
        self.__minimum_number_should_match__ = value
        self.__es_expr__["minimum_should_match"] = value

        return self

    def __neg__(self):
        ret = DocumentFields()
        ret.__es_expr__ = {"must_not": {"bool": {"filter": self.__es_expr__.get("filter") or self.__es_expr__}}}
        ret.__is_bool__ = True
        return ret

    def startswith(self, item):
        ret = DocumentFields()
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """

            ret.__es_expr__ = {
                "regexp": {
                    self.__name__: {
                        "value": r"^" + item + ".*",
                        "flags": "ALL"
                    }
                }
            }
            return ret
        else:
            raise Exception("Not support")

    def endswith(self, item):
        ret = DocumentFields()
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """
            item = __well_form__(item)
            ret.__es_expr__ = {
                "regexp": {
                    self.__name__: f".*{item}$"
                }
            }
            return ret
        else:
            raise Exception("Not support")

    def __contains__(self, item):
        ret = DocumentFields()
        # self.__is_bool__ = True
        if isinstance(item, str):
            """
            {
                  "query": {
                    "match_phrase": {
                      "message": "this is a test"
                    }
                  }
                }
            """
            import re
            # item = __well_form__(item)
            # if item[0:1]=='*' and item[-1]=='*':
            #     item="."+item[0:-1] +".*"
            # elif item[-1]=='*':
            #     item="^"+item[0:-1] +".*"
            # elif item[0:1]=='*':
            #     item="."+item+"$"
            # ret.__es_expr__ = {
            #     "regexp": {
            #         self.__name__: item
            #     }
            # }
            # ret.__es_expr__ = {
            #     "wildcard": {
            #         self.__name__: item
            #     }
            # }

            src = f"(doc['{self.__name__}.keyword'].size()>0) && doc['{self.__name__}.keyword'].value.contains(params.item)"
            if item[0] != '*' and item[-1] == '*':
                src = f"(doc['{self.__name__}.keyword'].size()>0) && (doc['{self.__name__}.keyword'].value.indexOf(params.item)==0)"
            elif item[0] == '*' and item[-1] != '*':
                src = f"(doc['{self.__name__}.keyword'].size()>0) && doc['{self.__name__}.keyword'].value.endsWith(params.item)"
            # value
            ret.__es_expr__ = {
                "filter": {
                    "script": {

                        "script": {

                            "source": f"return  {src};",
                            "lang": "painless",
                            "params": {
                                "item": item.lstrip('*').rstrip('*')
                            }
                        }
                    }
                }
            }
            ret.__is_bool__ = True
            fx_check_field = DocumentFields(self.__name__) != None
            ret = fx_check_field & ret
            ret.__highlight_fields__ = [self.__name__]
            return ret
        elif isinstance(item, list):
            """
            {
              "filtered": {
                "query": {
                  "match": { "title": "hello world" }
                },
                "filter": {
                  "terms": {
                    "tags": ["c", "d"]
                  }
                }
              }
            }
            """
            # key_words = '+ - && || ! ( ) { } [ ] ^ " ~ * ? : \\'.split(' ')
            # _item_ = []
            # for x in item:
            #     if isinstance(x,str):
            #         t =''
            #         for k in x:
            #             if k in key_words:
            #                 t+=f'\{k}'
            #             else:
            #                 t+=k
            #
            #         _item_+=[t]
            #     else:
            #         _item_ += [x]

            # ret.__es_expr__ = {
            #     "filter":{
            #         "terms": {
            #             self.__name__: _item_
            #         },
            #
            #     }
            # }
            src = ""

            for i in range(0, len(item)):
                src += f"doc['{self.__name__}.keyword'].contains(params.items[{i}])\n && "
            src = src.rstrip(' && ')
            ret.__es_expr__ = {
                "filter": {
                    "script": {

                        "script": {

                            "source": f"return  {src};",
                            "lang": "painless",
                            "params": {
                                "items": item
                            }
                        }
                    }
                }
            }

            ret.__is_bool__ = True
            fx_check_field = DocumentFields(self.__name__) != None
            return fx_check_field & ret
        else:
            raise Exception("Not support")

    def contains(self, *args):
        ret = DocumentFields()
        values = args
        if isinstance(values, tuple):
            values = list(values)

        self.__is_bool__ = True
        ret.__es_expr__ = {
            "terms": {
                self.__name__: values
            }
        }
        return ret

    def __getattr__(self, item):
        if item.lower() == "id":
            item = "_id"
        if self.__name__ is not None:
            return DocumentFields(f"{self.__name__}.{item}")
        return DocumentFields(item)

    def __or__(self, other):
        ret = DocumentFields()
        if isinstance(other, DocumentFields):
            if self.__wrap_func__:
                left = {"bool": {"filter": self.__es_expr__}}
            elif self.__is_bool__:

                left = {"bool": self.__es_expr__}
            else:
                left = self.__es_expr__
            if other.__wrap_func__:
                right = {"bool": {"filter": other.__es_expr__}}
            elif other.__is_bool__:

                right = {"bool": other.__es_expr__}
            else:
                right = other.__es_expr__

            ret.__es_expr__ = {
                "should": [
                    left, right
                ]
            }
            ret.__is_bool__ = True
            ret.__highlight_fields__ = list(set(self.__highlight_fields__ + other.__highlight_fields__))
            return ret
        elif isinstance(other, dict):
            if not self.__is_bool__:

                left = self.__es_expr__
                right = other

                ret.__es_expr__ = {
                    "should": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
            else:
                left = {"bool": self.__es_expr__}
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
        else:
            raise Exception("invalid expr")

    def __and__(self, other):

        ret = DocumentFields()
        if isinstance(other, DocumentFields):
            if self.__wrap_func__:
                left = {"bool": {"filter": self.__es_expr__}}
            elif self.__is_bool__:

                left = {"bool": self.__es_expr__}
            else:
                left = self.__es_expr__
            if other.__wrap_func__:
                right = {"bool": {"filter": other.__es_expr__}}
            elif other.__is_bool__:
                right = {"bool": other.__es_expr__}
            else:
                right = other.__es_expr__

            ret.__es_expr__ = {
                "must": [
                    left, right
                ]
            }
            ret.__is_bool__ = True
            ret.__highlight_fields__ = list(set(self.__highlight_fields__ + other.__highlight_fields__))
            return ret
        elif isinstance(other, dict):
            if not self.__is_bool__:
                left = self.__es_expr__
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
            else:
                left = {"bool": self.__es_expr__}
                right = other
                ret.__es_expr__ = {
                    "must": [
                        left, right
                    ]
                }
                ret.__is_bool__ = True
                return ret
        else:
            raise Exception("invalid expr")

    def __try_parse_date__(self, str_date):
        if not isinstance(str_date, str) or '+' not in str_date and str_date.__len__() >= 27:
            try:
                t = datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')

                return t, True
            except Exception as e:
                return None, False
        str_date_time = str_date.split('+')[0]
        try:
            t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
            tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
            ret = t + datetime.timedelta(tz.hour)
            return ret, True
        except Exception as e:
            return None, False

    def __eq__(self, other):

        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val

        if other is None:
            ret = DocumentFields()
            self.__is_bool__ = True

            ret.__es_expr__ = {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        elif isinstance(other, str):
            ret = DocumentFields()
            src = f"doc['{self.__name__}.keyword'].value==params.item"

            # value
            ret.__es_expr__ = {
                "filter": {
                    "script": {

                        "script": {

                            "source": f"return  {src};",
                            "lang": "painless",
                            "params": {
                                "item": other
                            }
                        }
                    }
                }
            }
            ret.__is_bool__ = True
            fx_check_field = DocumentFields(self.__name__) != None
            ret = fx_check_field & ret

            return ret

        elif type(other) in [int, float, datetime.datetime, bool]:

            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}==params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            else:
                ret = DocumentFields()
                ret.__es_expr__ = {
                    "term": {
                        self.__name__: other
                    }
                }
                return ret
        elif isinstance(other, list):
            ret = DocumentFields()
            ret.__es_expr__ = {
                "terms": {
                    self.__name__: other
                }
            }
            return ret
        else:

            raise Exception(f"{other} is not int,float or datetime")

    def __ne__(self, other):
        """

        :param other:
        :return:
        """
        """
        {
            "query" : {
                "constant_score" : {
                    "filter" : {
                        "bool": {
                            "must": {"exists": {"field": "<your_field_name_here>"}},
                            "must_not": {"term": {"<your_field_name_here>": ""}}
                        }
                    }
                }
            }
        }
        """
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if other is None:
            """
            {
              "query": {
                "bool": {
                  "must": {
                    "exists": {
                      "field": "myfield"
                    }
                  },
                  "must_not": {
                    "term": {
                      "myfield.keyword": ""
                    }
                  }
                }
              }
            }
            """
            ret = DocumentFields()
            self.__is_bool__ = True

            ret.__es_expr__ = {
                "bool": {
                    "must": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        if isinstance(other, str):
            ret = DocumentFields()
            src = f"doc['{self.__name__}.keyword'].value!=params.item"

            # value
            ret.__es_expr__ = {
                "filter": {
                    "script": {

                        "script": {

                            "source": f"return  {src};",
                            "lang": "painless",
                            "params": {
                                "item": other
                            }
                        }
                    }
                }
            }
            ret.__is_bool__ = True
            fx_check_field = DocumentFields(self.__name__) != None
            ret = fx_check_field & ret

            return ret
        else:
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}!=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "bool": dict(must_not=[{
                    "term": {
                        self.__name__: other

                    }
                }])
            }
            return ret

    def __matmul__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if other is None:
            ret = DocumentFields()
            self.__is_bool__ = True
            # es_object = __make_up_es__(self.__name__, other)
            ret.__es_expr__ = {
                "bool": {
                    "must_not": {
                        "exists": {
                            "field": self.__name__
                        }
                    }
                }
            }
            return ret
        elif isinstance(other, str):
            ret = DocumentFields()
            src = f"doc['{self.__name__}.keyword'].value==params.item"

            # value
            ret.__es_expr__ = {
                "filter": {
                    "script": {

                        "script": {

                            "source": f"return  {src};",
                            "lang": "painless",
                            "params": {
                                "item": other
                            }
                        }
                    }
                }
            }
            ret.__is_bool__ = True
            fx_check_field = DocumentFields(self.__name__) != None
            ret = fx_check_field & ret

            return ret
        else:
            ret = DocumentFields()
            ret.__es_expr__ = {
                "term": {
                    self.__name__: other
                }
            }
            return ret

    def __lt__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}<params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "lt": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __le__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}<=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "lte": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __gt__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}>params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "gt": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def __ge__(self, other):
        date_val, is_ok = self.__try_parse_date__(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
            ret = DocumentFields()
            ret = DocumentFields()
            if __check_is_painless_expr__(self.__es_expr__):
                key_name = self.__es_expr__["script"]["script"]['source']
                self.__es_expr__["script"]["script"]['source'] = f"{key_name}>=params.p"
                self.__es_expr__["script"]["script"]['params'] = {
                    "p": other
                }
                self.__is_bool__ = True
                return self
            ret.__es_expr__ = {
                "range": {
                    self.__name__: {
                        "gte": other
                    }
                }
            }
            return ret
        else:
            raise Exception(f"{other} is not int,float or datetime")

    def boost(self, value: float):
        if isinstance(self.__es_expr__, dict):
            self.__es_expr__["boost"] = value
        return self

    def __rshift__(self, other):
        ret = DocumentFields()
        ret.__es_expr__ = {
            "filter": {
                "simple_query_string": {
                    "fields": [self.__name__],
                    "query": other
                }}
        }
        ret.__is_bool__ = True
        return ret

    def __lshift__(self, other):
        if self.__name__ is None:
            raise Exception("Thous can not update expression")
        if other is not None:
            if type(other) not in [str, int, float, bool, datetime.datetime, dict, list]:
                raise Exception(
                    f"Thous can not update by non primitive type. {type(other)} is not in [str,str,int,float,bool,datetime.datetime,dict,list]")
        ret = DocumentFields(self.__name__)
        ret.__value__ = other
        ret.__has_set_value__ = True
        return ret

    def __repr__(self):
        if isinstance(self.__es_expr__, dict):
            jsonable = to_json_convertable(self.__get_expr__())
            return json.dumps(jsonable, indent=1)
        return self.__name__

    def __get_expr__(self):
        if isinstance(self.__es_expr__, dict):
            if self.__es_expr__.get('script') and isinstance(self.__es_expr__['script'].get('script'), dict) and \
                    self.__es_expr__['script']['script'].get('source'):
                ret = {
                    "bool": {
                        "filter": self.__es_expr__
                    }
                }
                return dict(query=ret)

            ret = self.__es_expr__
            if self.__name__ is not None:
                return {
                    "term": {
                        self.__name__: {
                            "value": self.__es_expr__
                        }
                    }
                }
            if self.__is_bool__:
                ret = {
                    "bool": ret
                }

            return dict(query=ret)
        return self.__name__

    def get_month(self):
        self.__wrap_func__ = "get_day_of_month"

        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getMonthValue()",
                    "lang": "painless"
                }
            }
        }

        return self

    def sub_string(self, start, end):
        self.__wrap_func__ = "sub_string"

        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.substring({start},{end})",
                    "lang": "painless"
                }
            }
        }
        return self

    def starts_with(self, words: str):

        """

        :param words:
        :return:
        """
        """
            {
              "query": {
                "match_phrase_prefix": {
                  "message": {
                    "query": "quick brown f"
                  }
                }
              }
            }
        """
        item = __well_form__(words)
        ret = DocumentFields()
        # ret.__wrap_func__ = "index_of"
        # ret.__is_bool__ = True
        ret.__es_expr__ = {
            "prefix": {
                self.__name__: words
            }

        }

        return ret

    def get_day_of_month(self):
        self.__wrap_func__ = "get_day_of_month"
        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getDayOfMonth()",
                    "lang": "painless"
                }
            }
        }

        return self

    def get_year(self):
        self.__wrap_func__ = "getYear"
        """
         {
              "query": {
                "bool" : {
                  "filter" : {
                   "script" : {
                      "script" : {
                        "source": "doc['timestampstring'].value.getHour() == 5",
                        "lang": "painless"
                      }
                    }
                  }
                }
              }
            }
        """
        k = "['" + self.__name__.replace('.', "']['") + "']"
        self.__es_expr__ = {
            "script": {
                "script": {
                    "source": f"doc['{self.__name__}'].value.getYear()",
                    "lang": "painless"
                }
            }
        }

        return self


def set_norms(field: DocumentFields, field_type: str, enable: bool) -> DocumentFields:
    return field.set_type(field_type).set_norms(enable)


def create_mapping(fields):
    properties = dict()
    for x in fields:
        if isinstance(x, DocumentFields):
            for k, v in x.get_mapping().items():
                properties[k] = v
    return dict(
        mappings=dict(
            properties=properties
        )
    )


"""
match_phraseBody = {
                "match_phrase": {
                    "content": {
                        "query": str_content,
                        "slop": 3,
                        "analyzer": "standard",
                        "zero_terms_query": "none",
                        "boost": 4.5
                    }
                }
            }
"""


def query_string(fields: typing.List[DocumentFields], query: str):
    return {
        "query_string": {
            "fields": [x.__name__ for x in fields],
            "query": query
        }
    }


def match(field: DocumentFields, content: str, boost=None, slop=None):
    """

    :return:
    """
    ret = DocumentFields()
    __match_content__ = {
        "match": {
            field.__name__: {
                "query": content
                # "boost": 0.5

            }
        }
    }

    if boost is not None:
        __match_content__["match"][field.__name__]["boost"] = boost
    # if slop is not None:
    #     __match_content__["match"][field.__name__]["slop"] = slop
    ret.__es_expr__ = __match_content__
    return ret


def wildcard(field: DocumentFields, content: str):
    """
    :return:
    """
    """
    "query": {
          "bool": {
              "should": [
                {
                  "wildcard": { "Field1": "*" + term + "*" }
                },
                {
                  "wildcard": { "Field2": "*" + term + "*" }
                }
              ],
              "minimum_should_match": 1
          }
      }
    """
    ret = DocumentFields()
    __match_phrase__ = {
        "wildcard": {
            field.__name__: "*" + content + "*"
        }
    }

    ret.__es_expr__ = {
        "match_phrase": __match_phrase__
    }

    # ret.__es_expr__["boost"] = boost
    return ret


def match_phrase(field: DocumentFields, content: str, boost=None, slop=None,
                 analyzer="standard") -> DocumentFields:
    ret = DocumentFields()
    __match_phrase__ = {
        field.__name__: {
            "query": content,
            "analyzer": analyzer,
            "zero_terms_query": "none"
        }
    }
    if boost is not None:
        __match_phrase__[field.__name__]["boost"] = boost
    if slop is not None:
        __match_phrase__[field.__name__]["slop"] = slop
    ret.__es_expr__ = {
        "match_phrase": __match_phrase__
    }

    # ret.__es_expr__["boost"] = boost
    return ret


__cach__index__ = {}


def get_map(cls: type):
    ret = {}
    for k, v in cls.__annotations__.items():
        if v == str:
            ret[k] = "text"
        elif v == bool:
            ret[k] = "boolean"
        elif v == int:
            ret[k] = "long"
        elif v == float:
            ret[k] = "double"
        else:
            ret[k] = {"type": "nested"}
    return dict(
        mappings=dict(
            properties=ret
        )
    )


class SearchResultHits(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    @property
    def total(self) -> int:
        return self.get('total').get('value') or 0

    @property
    def hits(self) -> typing.List[dict]:
        return self.get('hits') or []

    @property
    def max_score(self) -> float:
        return self.get('max_score') or 0


class SearchResult(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    @property
    def hits(self) -> SearchResultHits:
        return SearchResultHits(self.get('hits') or {'value': 0})

    @property
    def took(self) -> int:
        return self.get('took') or 0

    @property
    def items(self):
        for x in self.hits.hits:
            yield ESDocumentObject(x)


def get_docs(client: Elasticsearch, index: str, doc_type: str = "_doc", limit=100, _from=0):
    index = index.lower()
    res = client.search(index=index, doc_type="_doc", body={
        'size': limit,
        'from': _from,
        'query': {
            'match_all': {}
        }
    })
    if res.get("hits"):
        if res["hits"].get("hits"):
            for x in res["hits"]["hits"]:
                yield ESDocumentObject(x)
    return []


def select(client: Elasticsearch, index: str, doc_type: str = "_doc", fields=[], filter=None, sort=None, skip=0,
           limit=1000, highlight_fields=None) -> SearchResult:
    """
    Select some field in Elasticsearch index
    :param client:
    :param index:
    :param doc_type:
    :param fields:
    :param filter: is Dictionary or DocumentFields
    :param sort:
    :param skip:
    :param limit:
    :return:
    """
    index = index.lower()
    _select_fields_ = []
    if isinstance(fields, dict):
        _select_fields_ = list(fields.keys())

    if isinstance(fields, tuple) or isinstance(fields, list):
        _fields_ = list(fields)
        for x in _fields_:
            if isinstance(x, DocumentFields):
                _select_fields_ += [x.__name__]
            elif isinstance(x, str):
                _select_fields_ += [x]
    """
        {
          "query": {
            "match": {
              "user.id": "kimchy"
            }
          },
          "fields": [
            "user.id",
            "http.response.*",         
            {
              "field": "@timestamp",
              "format": "epoch_millis" 
            }
          ],
          "_source": false
        }
    """
    _filter_ = None
    if isinstance(filter, dict):
        _filter_ = dict(query=filter)

    elif isinstance(filter, DocumentFields):
        _filter_ = filter.__get_expr__()
    _sort = None
    if sort is not None:
        if isinstance(sort, list):
            for x in sort:
                if isinstance(x, DocumentFields):
                    _sort += x.__get_expr__() + ","
                elif isinstance(x, str):
                    _sort += x + ","
    elif isinstance(sort, str):
        _sort = _sort[:-1]

    body = _filter_
    body["fields"] = _select_fields_
    body["from"] = skip * limit
    body["size"] = limit
    if fields is not None:
        body["_source"] = False
    if highlight_fields is not None:
        if isinstance(highlight_fields, str):
            body["highlight"] = {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                "fields": {
                    highlight_fields: {}
                }
            }
        elif isinstance(highlight_fields, DocumentFields):
            body["highlight"] = {
                "pre_tags": ["<b>"],
                "post_tags": ["</b>"],
                "fields": {
                    highlight_fields.__name__: {}
                }
            }
        elif isinstance(highlight_fields, list):
            _highlight_fields_ = {}
            for x in highlight_fields:
                if isinstance(x, str):
                    _highlight_fields_[x] = {}
                elif isinstance(x, DocumentFields):
                    _highlight_fields_[x.__name__] = {}

            body["highlight"] = {
                "pre_tags": ["<_highlight_fields_>"],
                "post_tags": ["</_highlight_fields_>"],
                "fields": _highlight_fields_
            }
    ret = client.search(
        index=index, doc_type=doc_type, body=body, sort=_sort
    )

    return SearchResult(ret)


def get_map_struct(client: Elasticsearch, index: str):
    """
    get mapping of Elasticsearch index
    :param client:
    :param index:
    :return:
    """
    index = index.lower()
    map = get_mapping(client, index)
    map_index = map[index]['mappings']

    def get_properties(data: dict, prefix=None):
        keys = data['properties'].keys()
        ret = {}
        for k in keys:
            info = data['properties'][k]
            if info.get('properties'):
                s = get_properties(info, k)
                for k, v in s.items():
                    ret[k] = v
            else:
                if prefix:
                    ret[f"{prefix}.{k}"] = data['properties'][k]
                else:
                    ret[f"{k}"] = data['properties'][k]
        return ret

    ret = get_properties(map_index)
    return ret


def search(client: Elasticsearch,
           index: str,
           filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None,
           sort=None,
           doc_type: str = "_doc",
           logic_filter=None) -> SearchResult:
    index = index.lower()
    body = {}
    if isinstance(logic_filter, DocumentFields):
        if isinstance(filter, DocumentFields):
            filter = filter & logic_filter
        else:
            filter = logic_filter
    if isinstance(filter, dict):
        body = dict(query=filter)

    elif isinstance(filter, DocumentFields):
        body = filter.__get_expr__()

    body["from"] = skip * limit
    body["size"] = limit
    if len(excludes) > 0:
        body["_source"] = {
            "excludes": [x.__name__ for x in excludes]
        }
    """
    __highlight = {
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"],
                "fields": {
                    "content": {}
                }
            }
    """
    if highlight:
        """
        "highlight": {
    "require_field_match": "false",
    "fields": {
      "title": {},
      "email": {}
    }
  }
        """
        fields = {}
        for x in highlight:
            fields[x.__name__] = {}
        __highlight = {
            "require_field_match": False,
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
            "fields": fields
        }
        body["highlight"] = __highlight
    _sort = "_score:desc,"
    if sort is not None:
        if isinstance(sort, list):
            for x in sort:
                if isinstance(x, DocumentFields):
                    _sort += x.__get_expr__() + ","
                elif isinstance(x, str):
                    _sort += x + ","

    _sort = _sort[:-1]
    #
    # body["aggs"]= {
    #     "keywords" : {
    #         "significant_text" : {
    #             "field" : "content",
    #             "filter_duplicate_text": True,
    #             "min_doc_count":1
    #             }
    #         }
    # }
    try:
        ret = client.search(index=index, doc_type=doc_type, body=body, sort=_sort)
        return SearchResult(ret)
    except elasticsearch.exceptions.RequestError as e:
        print(body['query'])
        print(e.error)
        raise e
    except Exception as e:
        print(body['query'])
        print(e)
        raise e


docs = DocumentFields()


def is_index_exist(client: Elasticsearch, index: str):
    index = index.lower()
    return client.indices.exists(index)


class ESDocumentObject(dict):

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def get(self, key):

        if isinstance(key, DocumentFields):
            items = key.__name__split('.')
            ret = self
            for x in items:
                ret = dict.get(ret, x)
                if isinstance(ret, dict):
                    ret = ESDocumentObject(ret)
                if ret is None:
                    return None

            return ret
        else:
            return dict.get(self, key)

    def __getattr__(self, item):
        if isinstance(item, str) and item.lower() == "id":
            item = "_id"
        ret_val = self.get(item)
        if isinstance(ret_val, dict):
            return ESDocumentObject(**self.get(item))
        else:
            return ret_val

    def __setattr__(self, key, value):
        if isinstance(key, str) and key.lower() == "id":
            key = "_id"
        if isinstance(value, dict):
            dict.update(self, {key: ESDocumentObject(value)})

        else:
            dict.update(self, {key: value})

    def to_pydantic(self) -> pydantic.BaseModel:
        return pydantic.BaseModel(self)

    def to_dict(self) -> dict:
        ret = {}
        for k, v in self.items():
            if isinstance(v, ESDocumentObject):
                ret = {**ret, **{k: v.to_dict()}}
            else:
                ret = {**ret, **{k: v}}
        return ret

    def __repr__(self):
        import json
        return json.dumps(self.to_dict())


class ESDocumentObjectInfo:
    """
    {'_index': 'long-test-2011-11',
 '_type': '_doc',
 '_id': '56330233-59f2-48b9-b213-72e75f9f9b28',
 '_version': 4,
 '_seq_no': 3,
 '_primary_term': 1,
 'found': True,
 '_source': {'user_name': 'root',
  'password': 'tes',
  'tags': ['a', 'b', 'c', 'd']}}
    """

    def __init__(self, data):
        """

        :param data:
        """
        self.__data__ = data

    @property
    def __index__(self) -> str:
        return self.__data__["_index"]

    @property
    def id(self) -> str:
        return self.__data__["_id"]

    @property
    def doc_type(self) -> str:
        return self.__data__["_type"]

    @property
    def source(self) -> ESDocumentObject:
        return ESDocumentObject(self.__data__["_source"])


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> ESDocumentObjectInfo:
    index = index.lower()
    try:
        ret = client.get(index=index, id=id, doc_type=doc_type)
        return ESDocumentObjectInfo(data=ret)
    except elasticsearch.exceptions.NotFoundError as e:
        return None


def __convert_exception__(e):
    if isinstance(e, elasticsearch.RequestError):
        if e.status_code == 400 and e.error == "mapper_parsing_exception":
            if len(e.args) > 2:
                erros = e.args[2]
                if isinstance(erros.get('error'), dict):
                    if erros.get('error').get('root_cause') and isinstance(e.args[2].get('error').get('root_cause'),
                                                                           list) and len(
                        e.args[2].get('error').get('root_cause')) > 0:
                        if e.args[2].get('error').get('root_cause')[0].get('reason'):
                            return Exception(e.args[2].get('error').get('root_cause')[0].get('reason'))
    return e


def __es_create_index_if_not_exists__(es, index):
    """Create the given ElasticSearch index and ignore error if it already exists"""
    index = index.lower()
    try:
        es.indices.create(index, master_timeout='60s', timeout='60s', wait_for_active_shards=1)

        ret = es.indices.stats(index=index)

        return ret
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error == 'resource_already_exists_exception':
            es.indices.open(index=index)
            pass  # Index already exists. Ignore.
        else:  # Other exception - raise it
            raise ex


def __create_doc__(client: Elasticsearch, index: str, body: typing.Optional[typing.Union[dict, ESDocumentObjectInfo]],
                   id: str = None, doc_type: str = "_doc", es_type: str = None, try_count=30):
    try:
        index = index.lower()
        id = id or str(uuid.uuid4())
        if isinstance(body, ESDocumentObjectInfo):
            id = body.id or str(uuid.uuid4())
            body = body.source.to_dict()
        res = client.create(index=index, doc_type=doc_type, id=id, body=body)
        res["_source"] = body
        return ESDocumentObjectInfo(res), None
    except elasticsearch.RequestError as er:
        if er.status_code == 400:
            if try_count > 0:
                print(f"Create doc in {index} with id {id} fails, resume count ={try_count}")
                time.sleep(1)
                ret, error = __create_doc__(
                    client,
                    index,
                    body,
                    id,
                    doc_type,
                    es_type,
                    try_count - 1
                )
                return ret, error
            else:
                return None, er

        else:
            return None, er
    except Exception as e:
        return None, e


def create_doc(client: Elasticsearch, index: str, body: typing.Optional[typing.Union[dict, ESDocumentObjectInfo]],
               id: str = None, doc_type: str = "_doc", es_type: str = None):
    try:
        ret, error = __create_doc__(
            client=client,
            index=index,
            body=body,
            id=id,
            doc_type=doc_type,
            es_type=es_type
        )

        if error:
            raise error
        return ret
    except elasticsearch.exceptions.ConflictError as e:

        pass


def update_doc_by_id(client: Elasticsearch, index: str, id: str, data, doc_type: str = "_doc"):
    data_update = data
    if isinstance(data, DocumentFields):
        if data.__has_set_value__ is None:
            raise Exception(
                f"Hey!\n what the fu**king that?\n.thous should call {data.__name__} << {{your value}} ")
        data_update = {
            data.__name__: data.__value__
        }
    if isinstance(data, dict):
        data_update = data
    elif isinstance(data, tuple):
        data_update = {}

        for x in data:
            if isinstance(x, DocumentFields):
                if x.__has_set_value__ is None:
                    raise Exception(
                        f"Hey!\n what the fu**king that?\n.thous should call {x.__name__} << {{your value}} ")
                data_update[x.__name__] = x.__value__
    try:
        ret_update = client.update(
            index=index,
            id=id,
            doc_type=doc_type,
            body=dict(
                doc=data_update
            )

        )
        return data_update
    except elasticsearch.exceptions.NotFoundError as e:
        return None
    except Exception as e:
        for k in list(data_update.keys()):
            try:
                client.update(
                    index=index,
                    id=id,
                    doc_type=doc_type,
                    body=dict(
                        doc={
                            k: data_update[k]
                        }
                    )

                )
            except Exception as e:
                continue
        return data_update


def create_index(client: Elasticsearch, index: str, body: typing.Union[dict, type]):
    """
    Create new index if not exist
    :param client:
    :param index:
    :param body:
    :return:
    """
    index = index.lower()
    if client.indices.exists(index=index):
        """
        if exist return
        """
        return
    if inspect.isclass(body) and body not in [str, datetime.datetime, int, bool, float, int]:
        ret = client.indices.create(index=index, body=get_map(body))
        client.indices.open(index=index)
    else:
        ret = client.indices.create(index=index, body=body)
        client.indices.open(index=index)
    return ret


def delete_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):
    """
    Delete doc if exist
    :param client:
    :param index:
    :param id:
    :param doc_type:
    :return:
    """
    try:
        ret = client.delete(index=index, id=id, doc_type=doc_type)
        return ret
    except elasticsearch.exceptions.NotFoundError as e:
        return None


class __expr_type_enum__(Enum):
    """
    Private enum
    """
    CALL = 1
    """
    Function call
    """
    OPER = 2
    """
    Operand
    """
    LOGI = 3


__map__ = {
    "$and": dict(name="__and__", _type=__expr_type_enum__.LOGI),
    "$or": dict(name="__or__", _type=__expr_type_enum__.LOGI),
    "$contains": dict(name="contains", _type=__expr_type_enum__.CALL),
    "$first": dict(name="startswith", _type=__expr_type_enum__.CALL),
    "$last": dict(name="endswith", _type=__expr_type_enum__.CALL),
    "$not": dict(name="__neg__", _type=__expr_type_enum__.OPER),
    "$eq": dict(name="__matmul__", _type=__expr_type_enum__.OPER),
    "$lt": dict(name="__lt__", _type=__expr_type_enum__.OPER),
    "$lte": dict(name="__le__", _type=__expr_type_enum__.OPER),
    "$gt": dict(name="__gt__", _type=__expr_type_enum__.OPER),
    "$gte": dict(name="__ge__", _type=__expr_type_enum__.OPER),
    "$ne": dict(name="__ne__", _type=__expr_type_enum__.OPER)
}
"""
private const map operator to python class operator \n
toán tử bản đồ const riêng cho toán tử lớp python

"""


def __all_primitive__(x):
    """
    Check data type is primitive type \n
    Kiểm tra kiểu dữ liệu là kiểu nguyên thủy

    :param x:
    :return:
    """
    if type(x) in [str, int, float, bool, datetime.datetime]:
        return True
    elif isinstance(x, list):
        for v in x:
            if not __all_primitive__(v):
                return False
        return True


def nested(prefix: str, filter):
    """
    re-format filter with prefix \n
    Example: \n
        d = {"a$":1}
        nested("+",d)-> {"a+":1}
    :param prefix:
    :param filter:
    :return:
    """
    ret = {}
    if isinstance(filter, dict):
        for k, v in filter.items():
            _k = k
            _v = v
            if k[:1] != "$":
                _k = f"{prefix}.{_k}"
            if isinstance(v, dict):
                _v = nested(prefix, _v)
            elif isinstance(v, list):
                _v = [nested(prefix, x) for x in _v]
            ret[_k.lower()] = _v
            return ret
    return filter


def __clean_up__():
    try:
        import sys
        import ctypes
        if sys.platform == "linux":
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
    except Exception:
        pass


def loop_threading(loop_data: typing.Union[range, list, set, tuple]):
    import multiprocessing as mp
    from threading import Thread
    def __wrapper__(func: typing.Callable):

        def __start__(q: typing.List, x):
            ret = func(x)
            q.append(ret)

        def __run__(use_thread=True):
            if not use_thread:
                ret = []
                for row in loop_data:
                    ret += [func(row)]
                return ret

            ths = []
            q = []
            for row in loop_data:
                th = Thread(target=__start__, args=(q, row,))
                ths += [th]
                __clean_up__()

            for x in ths:
                x.start()
                __clean_up__()
            # for p in ths:
            #     ret = q.get()  # will block
            #     rets.append(ret)
            #     clean_up()
            for p in ths:
                p.join()
            __clean_up__()
            return q

        return __run__

    return __wrapper__


def hash_words(content: str, suggest_handler=None):
    words = content.lstrip(' ').rstrip(' ').replace('  ', ' ').split(' ')
    index_hash = []
    for i in range(0, len(words)):
        index_hash += [
            dict(
                index=i,
                # suggest_handler=suggest_handler,
                words=words

            )
        ]

    @loop_threading(index_hash)
    def calculate_hash(data: dict):
        left_len = len(data["words"]) - data["index"]
        right_len = data["index"] - len(data["words"])
        left = " ".join(data["words"][:left_len])
        right = " ".join(data["words"][right_len:])
        if suggest_handler:
            try:
                left_remain = suggest_handler(left)
            except Exception  as e:
                left_remain = left
            try:
                right_remain = suggest_handler(right)
            except Exception   as e:
                right_remain = right
        return (left,left_len), (right,-right_len), (left_remain,left_len), (right_remain,-right_len)

    ret = calculate_hash(False)
    return ret


def __build_search__depreciate_(fields, content, suggest_handler=None):
    """

    :param fields:
    :param content:
    :return:
    """
    """
    "query": {
    "multi_match" : {
      "query" : "this is a test",
      "fields" : [ "subject^3", "message" ] 
    }
  }
    """
    multi_match_ret = DocumentFields()
    match_fields = []
    list_of_hash = hash_words(content, suggest_handler)
    if callable(suggest_handler):
        suggest_content = suggest_handler(content)

    # for x in fields:
    #     if "^" in x:
    #         match_fields += [x]
    #     else:
    #         match_fields += [x, f"{x}_seg^2", f"{x}_bm25_seg^1"]

    fx_query_string_content_exactly = DocumentFields()
    content_exactly = []
    skip_count = 1
    for ((left,left_len),(right,right_len),(left_suggest,_),(right_suggest,_)) in list_of_hash:
        if left_len> skip_count:
            content_exactly += [
                {"constant_score":
                     {
                         "boost": 2000 * (left_len + 1),
                         "filter": {
                             "query_string": {
                                 "query": f'\"{left}\"  \"{left_suggest}\"',
                                 "fields": fields,
                                 "fuzziness": "0.5"
                }}}}
            ]
        if right_len > skip_count:
            content_exactly += [
                {"constant_score":
                    {
                        "boost": 2000 * (right_len + 1),
                        "filter": {
                            "query_string": {
                                "query": f'\"{right}\"  \"{right_suggest}\"',
                                "fields": fields,
                                "fuzziness": "0.5"
                            }}}}
            ]



    fx_query_string_content_exactly.__es_expr__ = {
        "should": content_exactly
    }
    fx_query_string_content_exactly.__is_bool__ = True

    # fx_query_string_content_suggest_exactly = DocumentFields()
    # fx_query_string_content_suggest_exactly.__es_expr__ = {
    #     "should": content_suggest_exactly
    # }
    # fx_query_string_content_suggest_exactly.__is_bool__ = True
    fx_query_string_content = DocumentFields()
    fx_query_string_content.__es_expr__ = {
        "must": {
            "query_string": {
                "query": content,
                "fields": fields
            }
        }
    }
    fx_query_string_content.__is_bool__ = True

    fx_query_string_content_suggest = DocumentFields()
    fx_query_string_content_suggest.__es_expr__ = {
        "must": {
            "query_string": {
                "query": suggest_content,
                "fields": fields,
                "min_term_freq": 1,
                "max_query_terms": 12
            }
        }
    }
    fx_query_string_content_suggest.__is_bool__ = True
    """
        {
            "query": {
                "more_like_this" : {
                    "fields" : ["title"],
                    "like" : "elasticsearch is fast",
                    "min_term_freq" : 1,
                    "max_query_terms" : 12
                }
            }
        
        }
    """
    fx_more_like_this = DocumentFields(is_bool=True)
    fx_more_like_this.__es_expr__ = {
        "must":{
            "more_like_this":{
                "fields":fields,
                "like": content,
                "min_term_freq": 1,
                "max_query_terms": 12,
                "boost":10000
            }
        }
    }
    fx_more_like_this.__highlight_fields__ = fields

    ret = fx_query_string_content_exactly | \
          fx_query_string_content
    ret =  fx_query_string_content
    return ret


def __build_search__(fields, content:str, suggest_handler=None):
    """

    :param fields:
    :param content:
    :return:
    """
    """
    "query": {
    "multi_match" : {
      "query" : "this is a test",
      "fields" : [ "subject^3", "message" ] 
    }
  }
    """
    content = content.replace('  ',' ').lstrip(' ').rstrip(' ')
    suggest_content = None
    suggest_search_content= None
    if callable(suggest_handler):
        suggest_content = suggest_handler(content)
    if suggest_content :
        suggest_words = suggest_content.replace('  ', ' ').lstrip(' ').rstrip(' ').split(' ')
        suggest_search_word = " ".join([f'(\"{x}\") AND' for x in suggest_words])
        suggest_search_word = suggest_search_word.rstrip('AND')
        suggest_search_content = f"(\"{suggest_content}\") OR (f{suggest_search_word})"

        # fx_suggest_query_string_content = DocumentFields(is_bool=True)
        # fx_suggest_query_string_content.__es_expr__ = {
        #     "must": {
        #         "query_string": {
        #             "query": suggest_search_content,
        #             "fields": fields,
        #             "boost": 500
        #         }
        #     }
        # }

    words = content.replace('  ',' ').lstrip(' ').rstrip(' ').split(' ')
    search_word = " ".join([f'(\"{x}\") AND' for x in words])
    search_word = search_word.rstrip('AND')
    search_content = f"(\"{content}\") OR (f{search_word})"
    if suggest_content != content and suggest_search_content:
        search_content = suggest_search_content

    fx_query_string_content = DocumentFields(is_bool=True)
    fx_query_string_content.__es_expr__ = {
        "must": {
            "query_string": {
                "query": search_content,
                "fields": fields,
                "boost":1000
            }
        }
    }

    ret = fx_query_string_content
    return ret


def __apply_function__(function_name, field_name, owner_caller=None, args=None, suggest_handler=None):
    """
    Private method \n
    Apply Function Call to DocumentFields
    The filter in JSON format (the JON format which use is pre compiler in to DocumentFields format) will change to DocumentFields format \n
    Phương thức riêng \n
    Áp dụng lệnh gọi hàm cho DocumentFields
    Bộ lọc ở định dạng JSON (định dạng JON sử dụng trình biên dịch trước ở định dạng DocumentFields) sẽ chuyển sang định dạng DocumentFields \n
    Exmaple: \n
        json = {
                 "$$day": {
                    "$field":"MyDate",
                    "$value": 22
                 }
            }
        will compiler to : DocumentFields.day(DocumentFields("Mydate"))==22 \n
    suggest_handler: An external function (JAVA or C# ,...) will convert Vietnamese none accents to Vietnamese with accents \n
    suggest_handler pair with $$search. It help $$search search Vietnamese non accents \n
    suggest_handler: Một hàm bên ngoài (JAVA hoặc C#,...) sẽ chuyển tiếng Việt không dấu sang tiếng Việt có dấu \n
    cặp suggest_handler với $$search. Nó giúp $$search tìm kiếm tiếng Việt không dấu \n
    The function can be convert are:
    $$day ,$$month, $$year, $$first, $$last, $$contains, $$search

    :param function_name:
    :param field_name:
    :param owner_caller:
    :param args:
    :param suggest_handler: An external function (properly in JAVA or C# ,...) will convert Vietnamese none accents to Vietnamese with accent
    :return:
    """
    if function_name == "$$day":
        ret = DocumentFields(field_name)
        return ret.get_day_of_month()
    elif function_name == "$$month":
        ret = DocumentFields(field_name)
        return ret.get_month()
    elif function_name == "$$year":
        ret = DocumentFields(field_name)
        return ret.get_year()
    elif function_name == "$$first":
        ret = DocumentFields(field_name)
        return ret.startswith
    elif function_name == "$$last":
        ret = DocumentFields(field_name)
        return ret.endswith
    elif function_name == "$$contains":
        if isinstance(field_name, dict):
            if field_name.get("$field") and field_name.get("$value"):
                ret = DocumentFields(field_name.get("$field"))
                return ret.__contains__(field_name.get("$value"))
            else:
                ret = DocumentFields(field_name)
                return ret.__contains__
    elif function_name == "$$search":
        if field_name.get("$field") and field_name.get("$value"):
            fields = field_name['$field']
            content = field_name['$value']
        else:
            fields = field_name['$fields']
            content = field_name['$value']

        return __build_search__(fields, content, suggest_handler)
    else:
        raise Exception("Error syntax")


def create_filter_from_dict(expr: dict, owner_caller=None, op=None, suggest_handler=None):
    """
    JSON Dictionary Filter use in Front-End like Web Browser
    Transform JSON Dictionary Filter into DocumentFields Filter \n
    Bộ lọc từ điển JSON sử dụng trong Front-End như Trình duyệt web
    Chuyển đổi Bộ lọc từ điển JSON thành Bộ lọc DocumentFields \n
    Example: \n
        {
            "$and":[
                    {
                    "$eq":{
                            "$$day":"data_item.CreatedOn","$value":2}},
                            {
                                "code":{"$eq":1}
                            }
                ]
        }
        ->
       (DocumentFields.day(DocumentFields("data_item").CreatedOn)==2)& \n
       (DocumentFields("code")==1)
    :param expr:
    :param owner_caller:
    :param op:
    :param suggest_handler:
    :return:
    """
    global __map__

    if isinstance(expr, dict):
        funcs = [x for x in expr.keys() if x.startswith('$$')]
        if op is not None and len(funcs) > 0 and expr["$value"] is not None:
            func_name = funcs[0]
            fx = __apply_function__(func_name, expr[func_name])
            if callable(fx) and not isinstance(fx, DocumentFields):
                fx = fx(expr["$value"])
                if func_name in ["$$first", "$$last", "$$contains"]:
                    return fx
            _op = op["name"]
            if _op == "__matmul__":
                _op = "__eq__"
            if hasattr(fx, _op):
                return getattr(fx, _op)(expr["$value"])

        for k, v in expr.items():
            if k[0:2] == "$$":
                ret = __apply_function__(k, v, owner_caller, suggest_handler=suggest_handler)
                if callable(ret) and not isinstance(ret, DocumentFields):
                    ret = ret(expr["$value"])
                    return ret
                elif op and op.get("name"):
                    _op = op.get("name")
                    if _op == "__matmul__":
                        _op = "__eq__"

                    caller = getattr(ret, _op)
                    ret = caller(expr["$value"])
                    return ret
                else:
                    # caller = getattr(ret, "__eq__")
                    # ret = caller(expr["$value"])
                    return ret
            elif k != "$value" and k[0:1] == "$":
                if not __map__.get(k):
                    raise Exception(f"{k} is Unknown")
                if __map__.get(k):
                    map_name = __map__[k]["name"]
                    if map_name == "__neg__":
                        ret = create_filter_from_dict(expr["$not"], suggest_handler=suggest_handler)
                        if not ret.__is_bool__:
                            __filter__ = DocumentFields()
                            __filter__.__es_expr__ = {
                                "filter": ret.__es_expr__
                            }
                            ret = __filter__
                        if hasattr(ret, map_name):
                            ret = getattr(ret, map_name)()
                            return ret
                        else:
                            raise Exception("Error syntax")

                    map_type: __expr_type_enum__ = __map__[k]["_type"]

                    if isinstance(v, list):
                        if __all_primitive__(v) and map_type == __expr_type_enum__.CALL:
                            ret = getattr(owner_caller, map_name)(*v)
                            return ret
                        else:
                            ret = create_filter_from_dict(v[0], suggest_handler=suggest_handler)
                            if len(v) > 1:
                                for i in range(1, len(v)):
                                    next = create_filter_from_dict(v[i], suggest_handler=suggest_handler)
                                    if map_type == __expr_type_enum__.LOGI:
                                        ret = getattr(ret, map_name)(next)
                                    else:
                                        # if owner_caller is not None:
                                        #     ret = getattr(owner_caller, method_name)(next)
                                        # else:
                                        raise NotImplemented
                            return ret
                    elif isinstance(v, dict):
                        ret = create_filter_from_dict(v, op=__map__[k], suggest_handler=suggest_handler)
                        return ret
                    elif isinstance(v, str):
                        ret = getattr(owner_caller, map_name)(v)
                        return ret


                    elif isinstance(v, str) and k == "$contains":
                        ret = getattr(owner_caller, "__contains__")(v)
                        return ret
                    else:
                        if map_type == __expr_type_enum__.OPER:
                            if isinstance(v, dict):
                                ret = create_filter_from_dict(v, suggest_handler=suggest_handler)
                                ret = getattr(ret, map_name)()
                                return ret
                            elif isinstance(owner_caller, DocumentFields):
                                handler = getattr(owner_caller, map_name)
                                ret = handler(v)
                                return ret
                            else:
                                raise NotImplemented
                        else:
                            raise NotImplemented

            else:
                if isinstance(v, dict):
                    ret = DocumentFields(k)
                    ret = create_filter_from_dict(v, ret, suggest_handler=suggest_handler)
                    return ret
                elif k == "$value" and op is not None and len([x for x in expr.keys() if x.startswith('$$')]) > 0:

                    ret = __apply_function__(k, v, owner_caller)
                    if callable(ret) and not isinstance(ret, DocumentFields):
                        ret = ret(expr["$value"])
                        return ret
                    elif op and op.get("name"):
                        _op = op.get("name")
                        if _op == "__matmul__":
                            _op = "__eq__"

                        caller = getattr(ret, _op)
                        ret = caller(expr["$value"])
                        return ret
                    else:
                        # caller = getattr(ret, "__eq__")
                        # ret = caller(expr["$value"])
                        return ret
                else:
                    ret = DocumentFields(k)
                    if op is not None:
                        _op = op["name"]
                        if _op == "__matmul__" and not isinstance(v, str):
                            _op = "__eq__"
                        if hasattr(ret, _op):
                            return getattr(ret, _op)(v)

                    ret = ret == v
                    return ret

    elif op is not None and isinstance(expr, dict) and expr["$value"]:
        lf = DocumentFields(list(expr.keys())[0])
        vf = expr[list(expr.keys())[0]]
        op_name = op["name"]
        if op_name == "__matmul__":
            op_name = "__eq__"
        return getattr(lf, op_name)(vf)

    else:
        raise NotImplemented


def is_exist(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> bool:
    """
    Check is exist doc with id
    :param client:
    :param index:
    :param id:
    :param doc_type:
    :return:
    """
    return client.exists(index=index, id=id, doc_type=doc_type)


def count(client: Elasticsearch, index: str):
    """
    Count all document in Elasticsearch
    :param client:
    :param index:
    :return:
    """
    ret = client.count(index=index)
    return ret.get('count', 0)


def clone_index(client: Elasticsearch, from_index, to_index, segment_size=100):
    """
    Clone index to new index
    :param client:
    :param from_index:
    :param to_index:
    :param segment_size:
    :return:
    """
    total_docs = count(client=client, index=from_index)

    i = 0
    while i < total_docs:
        ret_docs = get_docs(client, from_index, limit=segment_size, _from=i)
        for x in ret_docs:
            i += 1
            if not is_exist(client=client, index=to_index, id=x._id, doc_type=x._type):
                create_doc(
                    client=client,
                    index=to_index,
                    body=x._source,
                    id=x._id,
                    doc_type=x._type

                )

        print(f"{i}/{total_docs}")
    print("xong")


def put_mapping(client: Elasticsearch, index, body):
    """
    Put mapping
    :param client:
    :param index:
    :param body:
    :return:
    """
    return client.indices.put_mapping(
        index=index,
        body=body.get('mappings', body),
        ignore=400
    )


def get_mapping(client: Elasticsearch, index):
    """
    get mapping
    :param client:
    :param index:
    :return:
    """
    try:
        return client.indices.get_mapping(
            index=index,
            allow_no_indices=True
        )
    except elasticsearch.exceptions.NotFoundError as e:
        return None


def __fix_empty_value__(data):
    """
    ElasticSearch use null value somehow incorrect with language programming \n
    Example: default Null Value of text in ElasticSearch is "" \n
    Tìm kiếm đàn hồi sử dụng giá trị null bằng cách nào đó không chính xác với lập trình ngôn ngữ \n
    Ví dụ: Giá trị Null mặc định của văn bản trong Tìm kiếm đàn hồi là ""
    :param data:
    :return:
    """
    ret = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if k.endswith('_bm25_seg_vn_predict'):
                continue
            if isinstance(v, dict):
                if v.get('type') == 'text' and isinstance(v.get('fields'), dict) and isinstance(
                        v['fields'].get('keyword'), dict) and v['fields']['keyword']['type'] == 'keyword':
                    v['fields']['keyword']['null_value'] = ''
                else:
                    __fix_empty_value__(v)


def similarity_settings(client: Elasticsearch, index: str, field_name: str, algorithm_type: str, b_value, k1_value):
    """
    A similarity (scoring / ranking model) defines how matching documents are scored. Similarity is per field, meaning that via the mapping one can define a different similarity per field.

Configuring a custom similarity is considered an expert feature and the builtin similarities are most likely sufficient as is described in similarity.
    :param client:
    :param index:
    :param field_name:
    :param algorithm_type:
    :param b_value:
    :param k1_value:
    :return:
    """
    try:
        settings = client.indices.get_settings(index=index)
        settings_index = settings[index]
        if settings_index.get('settings') and settings_index['settings'].get('index') and settings_index['settings'][
            'index'].get('similarity') and settings_index['settings']['index']['similarity'].get('bm25_similarity'):
            try:
                client.indices.put_mapping(
                    index=index,
                    body=
                    {
                        "properties": {
                            field_name: {
                                "type": "text",
                                "similarity": "bm25_similarity",
                                "fielddata": True
                            },
                            f"{field_name}_lower": {
                                "type": "text",
                                "similarity": "bm25_similarity",
                                "fielddata": True
                            }

                        }
                    }
                )
            except Exception as e:
                print(e)




    except elasticsearch.exceptions.NotFoundError as e:
        client.indices.create(index=index)
    try:
        # settings[index]['settings']['index']['similarity']['bm25_similarity']
        client.indices.close(index=index)
        settings = {
            "index": {
                "similarity": {
                    "bm25_similarity": {
                        "type": algorithm_type,
                        "b": b_value,  # b gần về 0 sẽ bỏ qua độ dài của câu
                        "k1": k1_value
                    }
                }
            }
        }
        client.indices.put_settings(index=index, body=settings)
        client.indices.put_mapping(
            index=index,
            body=
            {
                "properties": {
                    field_name: {
                        "type": "text",
                        "similarity": "bm25_similarity",
                        "fielddata": True
                    }

                }
            }
        )
        client.indices.open(index=index)
    except Exception as e:
        print(e)


import bson


def to_json_convertable(data):
    """
    Sometime Dictionary Data can not portable to Front-End, Such as Dictionary Data contains BSON value.

    The method will fix it. \n
    Đôi khi Dữ liệu từ điển không thể di chuyển sang Front-End, chẳng hạn như Dữ liệu từ điển chứa giá trị BSON.

    Phương pháp sẽ sửa chữa nó.
    :param data:
    :return:
    """
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


def es_func_get_day(field):
    """
    Call dayOfMonth of ElasticSearch
    :return:
    """

    if isinstance(field, DocumentFields):
        """
       "script": {
            "script": "doc.readingTimestamp.date.getHourOfDay() >= 9 && doc.readingTimestamp.date.getHourOfDay() <= 18"
          } 
        """
        ret = dict(
            script={
                f"doc.{DocumentFields.__name__}.date.dayOfMonth"
            }
        )
        return ret
    raise NotImplemented()


def text_lower(filter):
    """
    Detect Filter if it has text then lower-case those text \n
    Phát hiện Bộ lọc nếu nó có văn bản thì viết thường những văn bản đó
    :param filter:
    :return:
    """
    if isinstance(filter, dict):
        ret = {}
        for k, v in filter.items():
            if isinstance(v, str):
                ret[k] = v.lower()
            elif isinstance(v, dict):
                ret[k] = text_lower(v)
            elif isinstance(v, list):
                ret[k] = []
                for x in v:
                    ret[k] += [text_lower(x)]
            else:
                ret[k] = v
        return ret
    elif isinstance(filter, str):
        return filter.lower()
    else:
        return filter


def create_dict_from_key_path_value(field_path: str, value):
    """
    Convert key, value pair to Dict \n
    Example:
        create_dict_from_key_path_value("a.b.c",1) \n
        {
            "a":{
                "b":{
                    "c": 1
                }
            }
        }
    :param field_path:
    :param value:
    :return:
    """
    if not "." in field_path:
        return {
            field_path: value
        }
    else:

        index = field_path.index(".")
        a = field_path[0:index]
        b = field_path[index + 1:]
        ret = create_dict_from_key_path_value(b, value)
        return {
            a: ret
        }


def update_data_fields(
        client: Elasticsearch, index: str,
        id: str,
        field_path=None,
        field_value=None,
        keys_values=None,
        doc_type="_doc"):
    """
    Update part of Elasticsearch document \n
    Example:
        update_data_fields(client,id,field_path="data_item.FileName",field_value="My File.mp4") \n
        update_data_fields(client,id,keys_values={
            "data_item":{
                "FileName":"My File.mp4"
            }
        }) \n
    :param client:
    :param index:
    :param id:
    :param field_path:
    :param field_value:
    :param keys_values:
    :param doc_type:
    :return:
    """
    try:

        keys_values = keys_values or {
            field_path: field_value
        }
        data = {}
        has_data = False
        for k, v in keys_values.items():
            if k != "_id":
                has_data = True
                d = create_dict_from_key_path_value(k, v)
                data = {**data, **d}
        if has_data:
            client.update(
                index=index,
                id=id,
                body={
                    "doc": data

                },
                doc_type=doc_type
            )
        return True

    except elasticsearch.exceptions.NotFoundError as e:
        return False


def flattern_dict(data, prefix=None):
    """
    Unwind all neat data to tabular data
    Example: d={
            "a":{
                "b":c
            }
    } -> {
        "a.b":c
    }
    :param data:
    :param prefix:
    :return:
    """
    if not isinstance(data, dict):
        raise Exception("data must be dict")
    ret = {}
    for k, v in data.items():
        if isinstance(v, dict):
            if prefix:
                s = flattern_dict(v, f"{prefix}.{k}")
            else:
                s = flattern_dict(v, k)
            ret = {**ret, **s}
        else:
            if prefix:
                ret = {**ret, **{f"{prefix}.{k}": v}}
            else:
                ret = {**ret, **{k: v}}
    return ret


def update_by_conditional(
        client: Elasticsearch,
        index: str,
        data_update,
        conditional,
        doc_type="_doc"
):
    """
    Update Elasticsearch by conditional\n
    conditional is DocumentFields or JSON dictionary\n
    Cập nhật Elaticsearch theo điều kiện\n
    có điều kiện là từ điển DocumentFields hoặc JSON
    :param client:
    :param index:
    :param data_update:
    :param conditional:
    :param doc_type:
    :return:
    """
    _data_update = to_json_convertable(data_update)
    body = {}

    if isinstance(conditional, DocumentFields):
        body = conditional.__get_expr__()
    if isinstance(conditional, dict):
        body = dict(query=conditional)
    inline_script = ""
    h = flattern_dict(_data_update)
    """
    {
      "script": {
        "inline": "ctx._source.student.hobbies.add(params.hobby); ctx._source.student.phone.add(params.phone)",
        "lang": "painless",
        "params": {
          "hobby": "cricket",
          "phone" : "122-33-4567"
        }
      }
    }
    """
    params = {
        "___obj___": dict()
    }
    for k, v in h.items():
        txt = ""
        p_k = k.replace('.', '_')
        items = k.split('.')
        if len(items) > 1:
            k1 = ""
            for x in items[:-1]:
                k1 += "." + x
                txt += f"if(ctx._source{k1}==null)\r\n {{\r\nctx._source{k1}=[:];\r\n}}\r\n"

        txt += f"ctx._source.{k}=params.{p_k};\r\n"

        inline_script += txt
        # inline_script += f"ctx._source.{k}=params.{p_k};"
        params[p_k] = v

    body["script"] = {
        "inline": inline_script,
        "lang": "painless",
        "params": params
    }

    ret = client.update_by_query(
        index=index,
        doc_type=doc_type,
        body=body

    )
    return ret.get("updated") or 0


def delete_by_conditional(client: Elasticsearch, index: str, conditional, doc_type="_doc"):
    """
    Delete documents by conditional \n
    conditional is DocumentFields or JSON dictionary
    :param client:
    :param index:
    :param conditional:
    :param doc_type:
    :return:
    """
    body = {}

    if isinstance(conditional, DocumentFields):
        body = conditional.__get_expr__()
    if isinstance(conditional, dict):
        body = dict(query=conditional)
    ret = client.delete_by_query(
        index=index,
        body=body, doc_type=doc_type

    )

    return ret.get("deleted") or 0


import uuid


def __is_date__(str_date):
    """
    Check is text in datetime format
    :param str_date:
    :return:
    """
    try:
        datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        return True
    except Exception as e:
        return False
    str_date_time = str_date.split('+')[0]
    try:
        t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
        tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
        ret = t + datetime.timedelta(tz.hour)
        return True
    except Exception as e:
        return False


def check_is_date(str_date: str) -> bool:
    """
        Check is text in datetime format
        :param str_date:
        :return:
        """
    return __is_date__(str_date)


def __is_valid_uuid__(value):
    try:
        uuid.UUID(value)

        return True
    except ValueError:
        return False


def check_is_guid(str_value: str) -> bool:
    """
    Check text is in GUID format
    :param str_value:
    :return:
    """
    return __is_valid_uuid__(str_value)


def is_content_text(text):
    """
    Check text is meaning text
    :param text:
    :return:
    """
    if isinstance(text, str) and not __is_date__(text) and not __is_valid_uuid__(text):
        return True
    return False


def convert_to_vn_predict_seg(data, handler, segment_handler, clear_accent_mark_handler):
    """
    Apply vn predict to Dictionary data \n

    :param data:
    :param handler:
    :param segment_handler:
    :param clear_accent_mark_handler:
    :return:
    """

    def add_more_content(data, handler, segment_handler, clear_accent_mark_handler):
        if isinstance(data, dict):
            ret = {}
            for k, v in data.items():
                x, y, z = add_more_content(v, handler, segment_handler, clear_accent_mark_handler)
                if y and y != x:
                    ret[f"{k}_vn_predict"] = y
                if z:
                    ret[f"{k}_bm25_seg"] = z
                ret[k] = x
            return ret, None, None
        elif isinstance(data, str):
            if not " " in data:
                return data, None, None
            if __is_valid_uuid__(data):
                return data, None, None
            elif __is_date__(data):
                return data, None, None
            else:
                vn_none_accent_content = clear_accent_mark_handler(data.lower())
                predict_content = handler(data)

                return data, predict_content, segment_handler(predict_content) + "/n" + segment_handler(
                    data) + "/n" + vn_none_accent_content
        elif isinstance(data, list):
            n_list = []
            for item in data:
                x, y, z = add_more_content(item, handler, segment_handler, clear_accent_mark_handler)
                if y and y != x:
                    n_list += [y]
                if z:
                    n_list += [z]
                n_list += [x]
            return n_list, None, None
        else:
            return data, None, None

    ret, _, _ = add_more_content(data, handler, segment_handler, clear_accent_mark_handler)
    return ret


def natural_logic_parse(expr: str):
    """
    Parse Expression Logic like a=b and c=d in to JSON like { "$and":[{ "a":{"$eq":b}},{"b":{"$eq":d}}] }
    :param expr:
    :return:
    """
    import ast
    expr = expr.replace('\n', ' ').replace('\t', ' ')

    def __convert_to_logical_text__(expr: str):
        """
        Pre process change = into == or something the programming language can undestand \n
        Thay đổi quá trình trước = thành == hoặc thứ gì đó mà ngôn ngữ lập trình không thể hiểu được
        :param expr:
        :return:
        """
        ret = expr
        while '  ' in ret:
            ret = ret.replace('  ', ' ')
        ret = expr.replace('=', '==')
        ret = ret.replace('===', '==')
        ret = ret.replace('>==', '>=')
        ret = ret.replace('<==', '<=')
        ret = ret.replace('<>', '!=')
        ret = ret.replace('!==', '!=')
        ret = ret.replace('not like ', '/=')
        ret = ret.replace(' like ', '<<')
        ret = ret.replace(' search ', '>>')
        return ret

    def __get_op__(node):
        """
        get operator
        :param node:
        :return:
        """
        if isinstance(node, ast.Eq):
            return "$eq"
        if isinstance(node, ast.NotEq):
            return "$ne"
        if isinstance(node, ast.Gt):
            return "$gt"
        if isinstance(node, ast.GtE):
            return "$gte"
        if isinstance(node, ast.Lt):
            return "$lt"
        if isinstance(node, ast.LtE):
            return "$lte"
        raise NotImplemented()

    def __get_name_of_ast__(node):
        """
        Convert AST to field name \n
        Example:
        Convert data_item.code -> "data_item.code" or data_item['code'] into data_item.code \n
        Chuyển đổi AST thành tên trường \n
        Ví dụ:
        Chuyển data_item.code -> "data_item.code" hoặc data_item['code'] thành data_item.code
        :param node:
        :return:
        """
        if isinstance(node, ast.Attribute):
            return f"{__get_name_of_ast__(node.value)}.{node.attr}"
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Subscript):
            return f"{__get_name_of_ast__(node.value)}.{__get_name_of_ast__(node.slice)}"
        if isinstance(node, ast.Constant):
            return node.value
        raise NotImplemented()

    def __resolve_call_node__(node):
        """
        Return function name and field name
        :param node:
        :return:
        """
        assert isinstance(node, ast.Call)
        func_name = f"$${node.func.id}"
        field_name = __get_name_of_ast__(node.args[0])
        return func_name, field_name

    def __parse_logical_expr__(node):
        """
        Parse Expression Logic like a=b and c=d in to JSON like { "$and":[{ "a":{"$eq":b}},{"b":{"$eq":d}}] }
        :param node:
        :return:
        """
        if isinstance(node, ast.List):
            ret = []
            for x in node.elts:
                ret += [__parse_logical_expr__(x)]
            return ret
        if isinstance(node, ast.BinOp) and type(node.op) == ast.LShift:
            left = __parse_logical_expr__(node.left)
            right = __parse_logical_expr__(node.right)
            function_name = None
            if isinstance(right, str) or isinstance(right, list):
                return {
                    "$$contains": {
                        "$field": left,
                        "$value": right
                    }
                }

            else:
                raise Exception("like operator only apply for text")
        if isinstance(node, ast.BinOp) and type(node.op) == ast.BitXor:
            field_name = __parse_logical_expr__(node.left)
            if isinstance(node.right, ast.BinOp):
                boost_score = __parse_logical_expr__(node.right.left)
                content_search = __parse_logical_expr__(node.right.right)
                return {
                    "$$search": {
                        "$fields": [f"{field_name}^{boost_score}"],
                        "$value": content_search
                    }
                }
            else:
                boost_score = __parse_logical_expr__(node.right)
                return f"{field_name}^{boost_score}"
        if isinstance(node, ast.BinOp) and type(node.op) == ast.RShift:
            if isinstance(node.left, ast.Tuple):
                left = []
                for x in node.left.dims:
                    left += [__parse_logical_expr__(x)]
                right = __parse_logical_expr__(node.right)
                function_name = None
                if isinstance(right, str):
                    return {
                        "$$search": {
                            "$fields": left,
                            "$value": right
                        }
                    }

                else:
                    raise Exception("like operator only apply for text")
            else:
                left = __parse_logical_expr__(node.left)
                right = __parse_logical_expr__(node.right)
                function_name = None
                if isinstance(right, str):
                    return {
                        "$$search": {
                            "$fields": [left],
                            "$value": right
                        }
                    }

                else:
                    raise Exception("like operator only apply for text")

        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Expr):
            return __parse_logical_expr__(node.value)
        if isinstance(node, ast.BoolOp):
            left = __parse_logical_expr__(node.values[0])
            right = __parse_logical_expr__(node.values[1])
            if type(node.op) == ast.And:
                return {
                    "$and": [left, right]
                }
            if type(node.op) == ast.Or:
                return {
                    "$or": [left, right]
                }
            raise NotImplemented()
        if isinstance(node, ast.Attribute):
            ret = __get_name_of_ast__(node)
            return ret
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Attribute) or isinstance(node.left, ast.Name):
                field_name = __get_name_of_ast__(node.left)
                field_value = __parse_logical_expr__(node.comparators[0])
                op = __get_op__(node.ops[0])
                return {
                    field_name: {
                        op: field_value
                    }
                }
            elif isinstance(node.left, ast.Call):
                function_name, field_name = __resolve_call_node__(node.left)
                field_value = __parse_logical_expr__(node.comparators[0])
                op = __get_op__(node.ops[0])
                ret = {
                    op: {
                        function_name: field_name,
                        "$value": field_value
                    }
                }
                return ret

            raise NotImplemented()
        if isinstance(node, ast.Name):
            ret = __get_name_of_ast__(node)
            return ret
        if isinstance(node, ast.Subscript):
            ret = __get_name_of_ast__(node)
            return ret
        if isinstance(node, ast.AugAssign) and type(node.op) == ast.Div:
            left = __parse_logical_expr__(node.target)
            right = __parse_logical_expr__(node.value)
            return {
                "$not": {
                    "$$contains": {
                        "$field": left,
                        "$value": right
                    }
                }
            }
        if isinstance(node, ast.UnaryOp) and type(node.op) == ast.Not:
            return {
                "$not": __parse_logical_expr__(node.operand)
            }

        raise NotImplemented()

    def parse_logic(expr: str):
        """
        Parse expr into DocumentFields \n
        Example:
        "(day(data_item.CreatedOn)=2) and (code=1)" -> (DocumentFields("data_item").CreatedOn==2)&(DocumentFields("Code")==1)
        :param expr:
        :return:
        """
        fx = __convert_to_logical_text__(expr)
        ret = ast.parse(fx)
        if ret.body.__len__() == 1:
            return __parse_logical_expr__(ret.body[0])

        raise NotImplemented()

    ret = parse_logic(expr)
    if not isinstance(ret, dict):
        raise Exception(f"'{expr}' is incorrect syntax")
    return ret


def delete_index(client: Elasticsearch, index: str):
    client.indices.delete(index=index, ignore=[400, 404])
