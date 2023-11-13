import re

from elasticsearch import Elasticsearch
import os
from  typing import List
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


def __well_form__(content: str) -> str:
    ch = ["+", "-", "*", "?", "|", "[", "]", "^", "$", "(", ")", "\\", "/", ".", ",", "!", "~", "<", ">", "%", "#",
          "@", ":"]
    ret =""
    for x in content:
        if x in ch:
            ret+=f"\\{x}"
        else:
            ret+=x

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


def __create_painless_source__(field_name:str, function_name:str):
    code_field_name = f"{field_name}"
    doc_field_key_word = f"doc['{code_field_name}.keyword']"
    doc_field = f"doc['{field_name}']"
    if function_name=="contains":
        """
        Debug.explain
        """
        src = f"({doc_field_key_word}.size()>0) && ({doc_field_key_word}.text.contains(params.item))"
        # src = f"({doc_field_key_word}.size()>0)"
        src2= f"({doc_field_key_word}.size()>0) && ctx._source['{field_name}'].contains(params.item)"
        src2 = f"({doc_field_key_word}.size()>0) && script.source.get('{field_name}').contains(params.item)"
        src='"Hello, world!".contains("hello")==true'
        """
            if (doc["log.keyword"].value == null) return false;
            return doc["log.keyword"].value.contains("Duplicate entry");
            """
        src = (f'if ({doc_field_key_word}.size()==0) return false;\n'
               f'if ({doc_field_key_word}.value == null) return false;\n'
               f'return {doc_field_key_word}.value.toLowerCase().toString().replace("\n", " ").replace("\t"," ").contains(params.item);')
        return src
    raise NotImplemented()

def __make_query_string__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    KIBANA_SPECIAL = '+ - & | ! ( ) { } [ ] ^ " ~ * ? : \\ = > <'.split(' ')
    ret = DocumentFields()
    import re
    __content__ = re.sub('([{}])'.format('\\'.join(KIBANA_SPECIAL)), r'\\\1', content)
    ret.__es_expr__ = {
        "must": {
            "query_string": {
                "query": __content__,
                "fields": [f"{field_name}"],
                "boost": boost_score,

            },

        },
        # "score_mode": "max"
    }
    ret.__is_bool__ = True
    ret.__highlight_fields__ =[field_name]
    return ret
def __make_script_contains__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    _src_ =("if(@field.size()==0){\n"
            "return false;"
            "}\n"
            "else{\n"
            "return @field.value.replace('\n',' ').replace('\t',' ').toLowerCase().indexOf(params.item)>-1;"
            "}")
    src =_src_.replace("@field",f"doc['{field_name}.keyword']")
    ret = DocumentFields()
    ret.__es_expr__ = {
        "filter": {
                        "script": {

                            "script": {

                                "source": f"{src}",
                                "lang": "painless",
                                "params": {
                                    "item": content.lower()
                                }

                            }

                        }
                    }
    }
    ret.__is_bool__ = True
    return ret
def __make_macth_pharse_script_score__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    ret = DocumentFields()
    score_source = ("if(@field.size()==0){\n"
                    "return 0;"
                    "}\n"
                    "else{\n"
                    "if(@field.value.contains(params.text_search)){"
                    "return 1.0;"
                    "}\n"
                    "else{\n"
                    "return 0;"
                    "}"
                    "}")

    ret.__es_expr__ = {
        "must": {
            "script_score": {
                "query": {
                    "match_phrase":{
                        field_name: __well_form__(content)
                    }
                },
                "script": {
                    "source": score_source.replace("@field",f"doc['{field_name}.keyword']"),
                    "params": {
                        "text_search": content
                    }
                }

        },
        # "score_mode": "max"
        }}
    ret.__is_bool__ = True
    ret.__highlight_fields__=[field_name]
    return ret

def __make_query_string_script_score__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    ret = DocumentFields()
    score_source = ("if(@field.size()==0){\n"
                    "return 0;"
                    "}\n"
                    "else{\n"
                    "if(@field.value.contains(params.text_search)){"
                    "return 1.0;"
                    "}\n"
                    "else{\n"
                    "return 0;"
                    "}"
                    "}")
    ret.__es_expr__ = {
        "must": {
            "function_score": {
                    "query": {
                        "query_string": {
                            "query": __well_form__(content),
                            "fields": [field_name]
                        }
                    },
                    "script_score": {
                        "script": {
                            "inline": score_source.replace("@field",f"doc['{field_name}.keyword']"),
                            "params": {
                                "text_search": content
                            }
                        }
                    }
                }

        },
        # "score_mode": "max"
    }
    ret.__is_bool__ = True
    ret.__highlight_fields__ =[field_name]
    return ret
def __make_wild_card__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    ret_keyword = DocumentFields()
    import re
    __content__ = re.escape(content)
    ret_keyword.__es_expr__ = {
        "must": {
            "wildcard": {
                f"{field_name}.keyword": {
                    "value": "*"+content+"*"
                }
            }

        },
        # "score_mode": "max"
    }
    ret_keyword.__is_bool__ = True
    ret_keyword.__highlight_fields__ = [field_name,f"{field_name}.keyword"]
    ret_field = DocumentFields()
    ret_field.__es_expr__ = {
        "must": {
            "wildcard": {
                f"{field_name}": {
                    "value": "*"+content+"*"
                }
            }

        },
        # "score_mode": "max"
    }
    ret_field.__is_bool__ = True
    ret= ret_field | ret_keyword
    ret.__highlight_fields__=[f"{field_name}",f"{field_name}.keyword"]
    return ret
def __make_pharse_edgeNGram__(field_name, content, boost_score):
    """
    {
          "query": {
            "bool": {
              "must": [
                {
                  "match_phrase": {
                    "field_name": {
                      "query": "!",
                      "analyzer": "edgeNGram"
                    }
                  }
                }
              ]
            }
          }
        }
    :return:
    """
    from cy_es.cy_es_docs import DocumentFields
    ret = DocumentFields()
    ret.__es_expr__ = {
        "must": {
            "match": {
            f"{field_name}": {
              "query": content,
              "analyzer": "keyword"
            }
          }

        }
    }
    ret.__highlight_fields__ = [field_name]
    ret.__is_bool__ = True
    return ret
def __make_regexp__(field_name, content, boost_score):
    from cy_es.cy_es_docs import DocumentFields
    ret_keyword = DocumentFields()
    ret_content = DocumentFields()

    KIBANA_SPECIAL = '+ - & | ! ( ) { } [ ] ^ " ~ * ? : \\ = > < / .'.split(' ')
    _content_ = re.sub('([{}])'.format('\\'.join(KIBANA_SPECIAL)), r'\\\1', content)
    ret_keyword.__es_expr__ = {
        "must": {
            "regexp":{
                f"{field_name}.keyword": {
                    "value":".*"+_content_+".*",
                    "flags": "ALL",
                    "case_insensitive": False,
                    "boost": boost_score - 250
                },
            }


        }
    }
    ret_keyword.__highlight_fields__ = [field_name,f"{field_name}.keyword"]
    ret_keyword.__is_bool__ = True
    ret_content.__es_expr__ = {
        "must": {
            "regexp": {
                f"{field_name}": {
                    "value": ".*" + _content_ + ".*",
                    "flags": "ALL",
                    "case_insensitive": False,
                    "boost": boost_score
                }

            }

        }
    }
    ret_content.__is_bool__ = True
    ret = ret_keyword | ret_content
    ret.__highlight_fields__ = [field_name, f"{field_name}.keyword"]
    return ret
def __make_like__(field_name, content, boost_score):
    """
    {
        "query": {
        "script_score": {
        "query": {
        "match_phrase": {
        "field_name": "Hello world"
        }
        },
        "script": {
        "source": "int max_length = 0; int phrase_count = 0; for (phrase in doc['field_name'].values()) { if (phrase.length > max_length) { max_length = phrase.length; } phrase_count++; } return phrase_count * max_length;"
        }
        }
        }
        }
    :param field_name:
    :param content:
    :param boost_score:
    :return:
    """
    # from cy_es.cy_es_docs import DocumentFields
    # ret = DocumentFields()
    # score_source = ("if(@field.size()==0){\n"
    #                 "return 0;"
    #                 "}\n"
    #                 "else{\n"
    #                 "if(@field.value.toLowerCase().contains(params.text_search)){"
    #                 "return 1000;"
    #                 "}\n"
    #                 "else{\n"
    #                 "return 0;"
    #                 "}"
    #                 "}")
    # ret.__es_expr__ = {
    #     "must": {
    #         "script_score": {
    #             "query": {
    #                 "match":{
    #                     field_name: __well_form__(content)
    #                 }
    #             },
    #             "script": {
    #                 "source": score_source.replace("@field",f"doc['{field_name}.keyword']"),
    #                 "params": {
    #                     "text_search": content
    #                 }
    #             }
    #
    #     },
    #     # "score_mode": "max"
    #     }}
    # ret.__is_bool__ = True
    # ret.__highlight_fields__=[field_name]
    ret_contains = __make_script_contains__(field_name=field_name,content=content,boost_score=0)
    ret_query = __make_query_string__(field_name=field_name,content=content,boost_score=1000)
    ret_macth_pharse_script = __make_macth_pharse_script_score__(field_name=field_name,content=content,boost_score=0)
    ret_wild_card = __make_wild_card__(field_name=field_name, content=content, boost_score=0)
    ret_script_score = __make_query_string_script_score__(field_name=field_name, content=content, boost_score=0)
    ret_match_phrase = __make_pharse_edgeNGram__(field_name=field_name, content=content, boost_score=0)
    ret_re = __make_regexp__(field_name=field_name, content=content, boost_score=1500)
    ret = ret_query | ret_wild_card | ret_re
    return  ret

