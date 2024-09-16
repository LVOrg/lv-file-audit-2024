from cy_es.cy_es_utils import (
    get_info,
    get_all_index,
    get_version,
    version,
    __check_is_painless_expr__,
    __make_up_es1__,
    __make_up_es_syntax__,
    __make_up_es_syntax_depriciate__,
    __well_form__
)
from cy_es_data_parser import try_parse_date

from cy_es_json import (
    to_json_convertable,
)
import datetime, json
from cy_es import es_script

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

    def __init__(self, name: str = None, is_bool=False):
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

    def __contains__2(self, item):
        ret = DocumentFields()
        field_name = self.__name__
        boost = None
        if "^" in field_name:
            field_name, boost = tuple(field_name.split("^"))

        if boost and boost.isnumeric():
            ret.__es_expr__ = {
                "must": {
                    "regexp": {
                        field_name: {
                            "value": f".*{item}.*",
                            "flags": "ALL",
                            "boost": boost
                        }
                    }}
            }
        else:
            ret.__es_expr__ = {
                "must": {
                    "regexp": {
                        field_name: {
                            "value": f".*{item}.*",
                            "flags": "ALL"
                        }
                    }}
            }
        ret.__is_bool__ = True
        return ret

    def __contains__(self, item):

        """

        @param item:
        @return:
        """

        ret = DocumentFields()
        field_name = self.__name__
        boost = None







        if "^" in field_name:
            field_name, boost = tuple(field_name.split("^"))
            if not  boost.isnumeric():
                boost=None
        ret.__d
        ret_match_phase=DocumentFields()
        ret_query = DocumentFields()
        dict_filter = es_script.script_index_of(field_name,item)
        if item[-1]=="*":
            dict_filter = es_script.script_start_with(field_name, item[:-1])
        elif item[0]=="*":
            dict_filter = es_script.script_end_with(field_name, item[1:])
        ret = es_script.build(ret,es_script.must_wrapper(es_script.constant_score(dict_filter,boost)))
        ret_match_phase = es_script.build(ret_match_phase,es_script.match_phrase(field_name,item,boost))
        ret_query = es_script.build(ret_query, es_script.simple_query_string(field_name, item, boost))
        ret=ret |ret_match_phase|ret_query
        ret.__highlight_fields__ = [field_name]
        return ret

    def __contains__delete(self, item):
        from cy_es.cy_es_utils import __well_form__

        import cy_es.cy_es_utils
        # special_characters = [
        #     "+", "-", "=", "&&", "||", ">", "<",
        #     "!" "(", ")", "{", "}", "[", "]", "^", "\"", "~", "*", "?", ":", "\\", "/"
        # ]

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

            field_name = self.__name__
            boost_score = 0.0
            query_value = ""
            first = ""
            last = ""
            code_field_name = f"{field_name}"
            doc_field_key_word = f"doc['{code_field_name}.keyword']"
            doc_field = f"doc['{field_name}']"
            if "^" in field_name:
                field_name = self.__name__.split("^")[0]
                boost_score = float(self.__name__.split("^")[1])

            src = cy_es.cy_es_utils.__create_painless_source__(field_name=field_name, function_name="contains")
            if item[0] != '*' and item[-1] == '*':
                query_value = item[:-1]
                last = "*"
                src = f"({doc_field_key_word}.size()>0) && ({doc_field_key_word}.value.toLowerCase().indexOf(params.item)==0)"
            elif item[0] == '*' and item[-1] != '*':
                query_value = item[1:-1]
                first = "*"
                src = f"({doc_field_key_word}.size()>0) && {doc_field_key_word}.value.toLowerCase().endsWith(params.item)"
            elif item[0] == '*' and item[-1] == '*':
                first = "*"
                last = "*"
                query_value = item[1:-1]
            else:
                query_value = item
                txt_search = query_value.replace("  ", " ").lstrip(" ").rstrip(" ")
                if field_name == "content" and " " in txt_search:
                    from cy_es.cy_es_objective import __build_search__
                    search_content = __build_search__(["content"], txt_search)

                    return search_content
            search_value = __well_form__(query_value)
            # for x in query_value:
            #     if x in special_characters:
            #         search_value += f"\\{x}"
            #     else:
            #         search_value += x
            # value
            """
            {
                "bool": {
                  "must": [
                    {
                      "query_string": {
                        "query": "*dove*",
                        "fields": [
                          "field1",
                          "Name"
                        ]
                      }
                    },
                    {
                      "query_string": {
                        "query": "*3.75oz*",
                        "fields": [
                          "field1",
                          "Name"
                        ]
                      }
                    }
                  ]
                }
              }
            """
            # ret_filter = DocumentFields()
            # ret_filter.__es_expr__ = {
            #     "must": [
            #         {
            #             "constant_score": {
            #                 "filter": {
            #                     "script": {
            #
            #                         "script": {
            #
            #                             "source": f"return  {src};",
            #                             "lang": "painless",
            #                             "params": {
            #                                 "item": item.lstrip('*').rstrip('*').lower()
            #                             }
            #
            #                         }
            #
            #                     }
            #                 }
            #             }
            #         }
            #     ]
            # }
            # ret_filter.__is_bool__ = True
            if first == "" and last == "":
                first = "*"
                last = "*"
            """
            {
                  "query": {
                    "bool": {
                      "must": [
                        {
                          "wildcard": {
                            "name": "*hello*"
                          }
                        },
                        {
                          "wildcard": {
                            "name": "*world*"
                          }
                        }
                      ]
                    }
                  }
                }
            """
            import urllib.parse
            query_string_boost = 1000
            if boost_score > 0:
                query_string_boost = boost_score
            ret2 = DocumentFields()
            ret2.__es_expr__ = {
                "must": {
                    "query_string": {
                        "query": search_value,
                        "fields": [f"{field_name}"],
                        # "minimum_should_match":len(search_value.lstrip(' ').rstrip(' ').replace('  ',' ').split(' ')),
                        # "allow_leading_wildcard": True,
                        # "default_operator": "AND",
                        "boost": query_string_boost,
                        # "analyze_wildcard": True

                    },

                },
                # "score_mode": "max"
            }
            ret.__es_expr__ = {
                "must": {
                    "wildcard": {
                        f"{field_name}.keyword": {
                            "value": f"{first}{query_value}{last}"
                        }
                    }

                },
                # "score_mode": "max"
            }

            # ret2.__es_expr__ = {
            #     "must": {
            #         "wildcard": {
            #             f"{field_name}": {
            #                 "value": f"{first}{query_value}{last}"
            #             }
            #         }
            #
            #     },
            #     # "score_mode": "max"
            # }
            # """
            #     {
            #       "query": {
            #         "regexp": {
            #           "user.id": {
            #             "value": "k.*y",
            #             "flags": "ALL",
            #             "case_insensitive": true,
            #             "max_determinized_states": 10000,
            #             "rewrite": "constant_score_blended"
            #           }
            #         }
            #       }
            #     }
            # """
            import re
            # if first=="*":
            #     first ="."+first
            # if last =="*":
            #     last = "." + last
            # fx=re.compile(
            #     f"{first}{search_value.lower()}{last}",
            #     re.RegexFlag.IGNORECASE|re.RegexFlag.DOTALL
            # )
            search_value = search_value.replace(" ", "\\s*")
            # ret.__es_expr__ = {
            #     "must": {
            #         "regexp": {
            #             f"{field_name}":{
            #                  "value": f"{first}{search_value.lower()}{last}",
            #                     "flags": "ALL",
            #                     "case_insensitive": False,
            #                     # "max_determinized_states": 10000,
            #                     # "rewrite": "constant_score_blended"
            #             }
            #
            #         },
            #     }
            #     # "score_mode": "max"
            # }

            ret.__is_bool__ = True
            ret2.__is_bool__ = True
            # fx_check_field = DocumentFields(field_name) != None
            # ret = fx_check_field & ret
            ret.__highlight_fields__ += [field_name, f"{field_name}.keyword"]
            ret_return = ret2 | ret
            ret_return.__highlight_fields__ += [field_name, f"{field_name}.keyword"]
            ret_macth_pharse = cy_es.cy_es_utils.__make_like__(field_name=field_name, content=query_value,
                                                               boost_score=boost_score)

            return ret_macth_pharse
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

    def __eq__(self, other):

        date_val, is_ok = try_parse_date(other)
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
            elif isinstance(self.__es_expr__, dict) and isinstance(self.__es_expr__.get("must"), list) and \
                    len(self.__es_expr__["must"]) > 1 and \
                    isinstance(self.__es_expr__["must"][1].get("bool"), dict) and \
                    __check_is_painless_expr__(self.__es_expr__["must"][1]["bool"]["filter"]):
                key_name = self.__es_expr__["must"][1]["bool"]["filter"]["script"]["script"]['source']
                self.__es_expr__["must"][1]["bool"]["filter"]["script"]["script"]['source'] = f"{key_name}==params.p"
                self.__es_expr__["must"][1]["bool"]["filter"]["script"]["script"]['params'] = {
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
        date_val, is_ok = try_parse_date(other)
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
        date_val, is_ok = try_parse_date(other)
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
        date_val, is_ok = try_parse_date(other)
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
        date_val, is_ok = try_parse_date(other)
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
        date_val, is_ok = try_parse_date(other)
        if is_ok:
            other = date_val
        if type(other) in [int, float, datetime.datetime]:
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
        date_val, is_ok = try_parse_date(other)
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

    def to_nested(self):

        # ret = DocumentFields()
        # """
        # {
        #   "query": {
        #     "nested": {
        #       "path": "items",
        #       "query": {
        #         "bool": {
        #           "must": [
        #             { "match": { "items.text": "car" }},
        #             { "match": { "items.rank": 1 }}
        #           ]
        #         }
        #       }
        #     }
        #   }
        # }
        #
        # """
        # ret.__es_expr__ = {
        #     "filter":{
        #     "nested":{
        #         "path": self.__es_expr__['must']['query_string']['fields'][0],
        #         "query":{
        #             "bool":{
        #                 "must":[
        #                     { "match":                            self.__es_expr__['must']['query_string']['query'] }
        #                 ]
        #             }
        #         }
        #     }
        #     }
        # }
        # ret.__is_bool__ = True
        # ret.__highlight_fields__  =self.get_highlight_fields()
        self.__es_expr__['must']['query_string']['fields'] = [
            self.__es_expr__['must']['query_string']['fields'][0] + ".*"]
        return self
