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