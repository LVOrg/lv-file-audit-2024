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
import datetime
import pathlib
import sys

import cy_es

sys.path.append(
    pathlib.Path(__file__).parent.__str__()
)
from elasticsearch import Elasticsearch
import typing
import cy_es_x

DocumentFields = cy_es_x.DocumentFields
buiders = cy_es_x.docs


def create_index(client: Elasticsearch, index: str, body=None):
    """
    Create new index if not exist
    :param client:
    :param index:
    :param body:
    :return:
    """
    return cy_es_x.create_index(
        index=index,
        body=body,
        client=client
    )


def get_map_struct(client: Elasticsearch, index: str) -> dict:
    """
    get mapping of Elasticsearch index
    :param client:
    :param index:
    :return:
    """
    return cy_es_x.get_map_struct(client, index)


def select(
        client: Elasticsearch,
        index: str,
        doc_type: str = "_doc",
        fields=[],
        filter: typing.Union[dict,DocumentFields] = None ,
        sort=None,
        skip=0,
        limit=1000,
        highlight_fields=None
):
    """
    Select some field in Elasticsearch index \n
    Chọn một số trường trong chỉ mục Elaticsearch
    :param client:
    :param index:
    :param doc_type:
    :param fields: List of fields Example ["a","b.c"]
    :param filter:
    :param sort:
    :param skip:
    :param limit:
    :return:
    """
    return cy_es_x.select(
        client=client,
        index=index,
        doc_type=doc_type,
        filter=filter,
        fields=fields,
        sort=sort,
        skip=skip,
        limit=limit,
        highlight_fields= highlight_fields
    )


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
    return cy_es_x.search(
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


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    return cy_es_x.get_doc(client, index, id, doc_type=doc_type)


def delete_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):
    return cy_es_x.delete_doc(client=client, index=index, id=id, doc_type=doc_type)


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


ESDocumentObjectInfo = cy_es_x.ESDocumentObjectInfo
def create_doc(client: Elasticsearch, index: str, id: str, body :typing.Optional[typing.Union[dict,ESDocumentObjectInfo]],
               doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:


    return cy_es_x.create_doc(
        client=client,
        index=index,
        doc_type=doc_type,
        body=body,
        id=id
    )


match_phrase = cy_es_x.match_phrase
match = cy_es_x.match
query_string = cy_es_x.query_string


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


def update_doc_by_id(client: Elasticsearch, index: str, id: str, data, doc_type: str = "_doc"):
    """
    Update document \n
    Example: \n
        cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=upload_id,
                data=(
                    cy_es.buiders.privileges << privileges,
                    cy_es.buiders.meta_info << meta_info
                )
        )
    :param client:
    :param index:
    :param id:
    :param data:
    :param doc_type:
    :return:
    """
    return cy_es_x.update_doc_by_id(
        client=client,
        index=index,
        id=id,
        data=data,
        doc_type=doc_type
    )


def nested(field_name: str, filter: dict):
    return cy_es_x.nested(prefix=field_name, filter=filter)


def create_filter_from_dict(filter: dict, suggest_handler=None):
    if filter == {}:
        return None
    return cy_es_x.create_filter_from_dict(filter, suggest_handler=suggest_handler)


def is_exist(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> bool:
    return cy_es_x.is_exist(
        client=client,
        index=index,
        id=id,
        doc_type=doc_type
    )


def get_docs(client: Elasticsearch, index: str, doc_type: str = "_doc"):
    return cy_es_x.get_docs(
        client=client,
        index=index,
        doc_type=doc_type
    )


def create_mapping(fields: typing.List[cy_es_x.DocumentFields]):
    return cy_es_x.create_mapping(fields)


def set_norms(field: cy_es.buiders, field_type: str, enable: bool):
    return cy_es_x.set_norms(
        field=field,
        enable=enable,
        field_type=field_type
    )


def create_mapping_meta(client: Elasticsearch, index: str, body):
    ret = cy_es_x.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)


def put_mapping(client: Elasticsearch, index: str, body):
    ret = cy_es_x.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)


def get_mapping(client, index):
    return cy_es_x.get_mapping(
        client, index
    )


def text_lower(filter):
    return cy_es_x.text_lower(
        filter
    )


def create_dict_from_key_path_value(field_path: str, value):
    """
    Ex: field_path="a.b.c" value:1 =>{a:{b:{c:1}}
    :param field_path:
    :param value:
    :return:
    """
    return cy_es_x.create_dict_from_key_path_value(field_path, value)


def update_data_fields(client: Elasticsearch, index: str, id: str, field_path=None, field_value=None, keys_values=None):
    return cy_es_x.update_data_fields(
        client=client,
        index=index,
        id=id,
        field_path=field_path,
        field_value=field_value,
        keys_values=keys_values
    )


def update_by_conditional(
        client: Elasticsearch, index: str,
        data_update,
        conditional,
        doc_type="_doc"
):
    return cy_es_x.update_by_conditional(
        client=client,
        data_update=data_update,
        conditional=conditional,
        doc_type=doc_type,
        index=index
    )


def delete_by_conditional(client, index, conditional, doc_type="_doc"):
    return cy_es_x.delete_by_conditional(
        client=client,
        conditional=conditional,
        index=index,
        doc_type=doc_type
    )


import uuid


def is_content_text(text):
    return cy_es_x.is_content_text(text)


def convert_to_vn_predict_seg(data, handler, segment_handler, clear_accent_mark_handler):
    ret = cy_es_x.convert_to_vn_predict_seg(data, handler, segment_handler, clear_accent_mark_handler)
    return ret


def natural_logic_parse(expr):
    ret = cy_es_x.natural_logic_parse(expr)
    if not isinstance(ret, dict):
        raise Exception(f"'{expr}' is incorrect syntax")
    return ret


def parse_expr(expr: str, suggest_handler=None) -> DocumentFields:
    ret_dict = cy_es_x.natural_logic_parse(expr)
    ret = cy_es_x.create_filter_from_dict(
        expr=ret_dict,
        suggest_handler=suggest_handler,

    )
    return ret

delete_index = cy_es_x.delete_index
get_info  = cy_es_x.get_info
get_version = cy_es_x.get_version