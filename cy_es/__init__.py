"""
This is a crucial library when developer use Python to interact with Elasticsearch \n
Specially, for real complex  Elasticsearch filter the developer can not control the Filter with Elasticsearch format\n
    Đây là một thư viện quan trọng khi nhà phát triển sử dụng Python để tương tác với Elaticsearch \n
Đặc biệt, đối với bộ lọc Elaticsearch phức tạp thực sự, nhà phát triển không thể kiểm soát Bộ lọc có định dạng Elaticsearch\n
Example:\n
print(cy_es.DocumentFields("data_item").code==1 \n
Will change to \n
         { \n
         "query": { \n
          "term": { \n
           "data_item.code": 1 \n
          }
         }
        }
-------------------------- \n
Or Developer can use \n

fx=cy_es.buiders.data_item.code==1 \n
print(fx) \n
----------------------------------------- \n
Check data_item of document is existing then filter data-item.FileName contains '*.mp4' ? \n
fx = (cy_es.buiders.data_item != None) & (cy_es.buiders.data_item) \n
will generate ES filter like : \
    {
     "query": {
      "bool": {
       "must": [
        {
         "bool": {
          "must": {
           "exists": {
            "field": "data_item"
           }
          }
         }
        },
        {
         "wildcard": {
          "data_item.FileName": "*.mp4"
         }
        }
       ]
      }
     }
    }

--------------------------------------------------------------\n
or:
fx= cy_es.parse_expr("data_item !=None and data_item.code=1")

"""
import asyncio
import datetime
import pathlib
import sys

import cy_es

sys.path.append(
    pathlib.Path(__file__).parent.__str__()
)
from elasticsearch import Elasticsearch
import typing

import cy_es_json, cy_es_docs, cy_es_utils, cy_es_objective

DocumentFields = cy_es_docs.DocumentFields
buiders = cy_es_objective.docs

create_index = cy_es_objective.create_index
get_map_struct = cy_es_objective.get_map_struct
select = cy_es_objective.select

__cache__settings_max_result_window___ = {}
"""
Cache index settings
"""


def search(client: Elasticsearch,
           index: str,
           filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None,
           sort=None,
           doc_type="_doc",
           logic_filter=None):
    """
    Search content in ElasticSearch \n
    Example:
        search(client,index,filter={ "code":{"$eq":1}  })
        search(client,index,logic_filter={ "code":{"$eq":1}  })

    :param client:
    :param index:
    :param filter:
    :param excludes:
    :param skip:
    :param limit:
    :param highlight:
    :param sort:
    :param doc_type:
    :param logic_filter:
    :return:
    """
    global __cache__settings_max_result_window___
    if __cache__settings_max_result_window___.get(index) is None:
        client.indices.put_settings(index=index,
                                    body={"index": {
                                        "max_result_window": 50000000
                                    }})
        __cache__settings_max_result_window___[index] = True
    return cy_es_objective.search(
        client=client,
        index=index,
        excludes=excludes,
        skip=skip,
        limit=limit,
        highlight=highlight,
        filter=filter,
        sort=sort,
        logic_filter=logic_filter
    )


async def search_async(client: Elasticsearch,
                       index: str,
                       filter,
                       excludes: typing.List[DocumentFields] = [],
                       skip: int = 0,
                       limit: int = 50,
                       highlight: DocumentFields = None,
                       sort=None,
                       doc_type="_doc",
                       logic_filter=None):
    ret = search(
        client,
        index,
        filter,
        excludes,
        skip,
        limit, highlight, sort, doc_type, logic_filter
    )
    return ret


get_doc = cy_es_objective.get_doc
delete_doc = cy_es_objective.delete_doc
create_doc = cy_es_objective.create_doc

__check_mapping__ = {}


def __create_mapping_from_dict__(body):
    ret = {}
    for k, v in body.items():
        if v:
            if isinstance(v, int):
                ret[k] = {
                    "type": "long",
                    # "ignore_malformed": True
                }
            elif isinstance(v, float):
                ret[k] = {
                    "type": "float",
                    # "ignore_malformed": True
                }
            elif isinstance(v, datetime.datetime):
                ret[k] = {
                    "type": "date",
                    "ignore_malformed": True
                }
            elif isinstance(v, bool):
                ret[k] = {
                    "type": "boolean",
                    # "ignore_malformed": True
                }
            elif isinstance(v, str):
                ret[k] = {
                    "type": "text",
                    # "ignore_malformed": True
                }
            else:
                ret[k] = {
                    "type": "nested",
                    "dynamic": True
                }
    return {
        "properties": ret
    }


ESDocumentObjectInfo = cy_es_objective.ESDocumentObjectInfo

match_phrase = cy_es_objective.match_phrase
match = cy_es_objective.match
query_string = cy_es_objective.query_string
wildcard = cy_es_objective.wildcard
update_doc_by_id = cy_es_objective.update_doc_by_id
nested = cy_es_objective.nested
create_filter_from_dict = cy_es_objective.create_filter_from_dict


def is_exist(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> bool:
    if index == "True" or index == True:
        raise Exception("error index type")
    return cy_es_objective.is_exist(
        client=client,
        index=index,
        id=id,
        doc_type=doc_type
    )


get_docs = cy_es_objective.get_docs
create_mapping = cy_es_objective.create_mapping
set_norms = cy_es_objective.set_norms


def create_mapping_meta(client: Elasticsearch, index: str, body):
    ret = cy_es_objective.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)


def put_mapping(client: Elasticsearch, index: str, body):
    ret = cy_es_objective.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)

get_mapping = cy_es_objective.get_mapping

text_lower = cy_es_objective.text_lower
create_dict_from_key_path_value = cy_es_objective.create_dict_from_key_path_value
update_data_fields = cy_es_objective.update_data_fields
update_by_conditional = cy_es_objective.update_by_conditional
delete_by_conditional = cy_es_objective.delete_by_conditional
is_content_text = cy_es_objective.is_content_text
convert_to_vn_predict_seg = cy_es_objective.convert_to_vn_predict_seg
natural_logic_parse = cy_es_objective.natural_logic_parse



async def natural_logic_parse_async(expr):
    ret = await cy_es_objective.natural_logic_parse_async(expr)
    if not isinstance(ret, dict):
        raise Exception(f"'{expr}' is incorrect syntax")
    return ret


def parse_expr(expr: str, suggest_handler=None) -> DocumentFields:
    ret_dict = cy_es_objective.natural_logic_parse(expr)
    ret = cy_es_objective.create_filter_from_dict(
        expr=ret_dict,
        suggest_handler=suggest_handler,

    )
    return ret
delete_index = cy_es_objective.delete_index
async def get_doc_async(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):
    return get_doc(client, index, id, doc_type)
def __to_dict__(key,value):
    k=key.split('.')[0]
    m=".".join(key.split('.')[1:])
    if m=="":
        return {k:value}
    else:
        v=__to_dict__(m,value)
        return {k:v}

def replace_content(client:Elasticsearch, index:str, id:str, field_path, field_value,timeout="60s"):
    from cy_es.cy_es_manager import FIELD_RAW_TEXT,update_mapping
    data_raw_mapping_update = __to_dict__(f"{FIELD_RAW_TEXT}.{field_path}", field_value)
    data_mapping_update = __to_dict__(f"{field_path}", field_value)
    data_update = {**data_mapping_update,**data_raw_mapping_update}
    update_mapping(
        client=client,
        index=index,
        data=data_update
    )

    update_body_like = {
        "script": {
                "source": f"ctx._source.{FIELD_RAW_TEXT}.{field_path} = params.new_value",
                "params": {
                    "new_value": field_value
                },
            "lang": "painless",
            },

    }
    update_body = {
        "script": {
            "source": f"ctx._source.{field_path} = params.new_value",
            "params": {
                "new_value": field_value
            }
        },

    }
    try:
        response = client.update(index=index, id=id, body=update_body_like,doc_type="_doc",timeout=timeout)
    except Exception as e:

        update_body_like = {
            "doc": data_raw_mapping_update
        }
        response = client.update(index=index, id=id, body=update_body_like, doc_type="_doc",timeout=timeout)
    try:
        response = client.update(index=index, id=id, body=update_body, doc_type="_doc",timeout=timeout)
    except Exception as e:
        data_update = __to_dict__(field_path, field_value)
        update_body = {
            "doc": data_mapping_update
        }
        response = client.update(index=index, id=id, body=update_body, doc_type="_doc",timeout=timeout)
    return True