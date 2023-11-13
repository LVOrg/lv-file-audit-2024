import typing

import elasticsearch


def get_mapping(client: elasticsearch.Elasticsearch, index: str) -> typing.Optional[dict]:
    ret = client.indices.get_mapping(
        index=index
    )
    if not isinstance(ret, dict):
        return None
    if isinstance(ret.get(index), dict):
        if isinstance(ret.get(index).get("mappings"), dict):
            return ret[index]["mappings"]
    return None


def __extract__(mapping: dict, key: typing.Optional[str] = None):
    ret = []
    for k, v in mapping.get('properties', {}).items():
        if isinstance(k,str) and k.endswith("_bm25_seg"):
            continue
        if isinstance(k,str) and k.endswith("_bm25_bm25_seg"):
            continue
        if isinstance(k,str) and k.endswith("_bm25_seg_bm25_seg"):
            continue
        if isinstance(k,str) and k.endswith("_bm25_seg_vn_predict"):
            continue
        if isinstance(k,str) and k.endswith("_bm25_seg_vn_predict"):
            continue
        if isinstance(k,str) and k.endswith("_vn_predict"):
            continue
        if isinstance(v, dict):
            if isinstance(v.get("fields"), dict):
                if isinstance(v.get("fields").get("keyword"), dict):
                    if key:
                        ret += [f"{key}.{k}"]
                    else:
                        ret += [k]
                    continue
            if isinstance(v.get("properties"),dict):
                if key is None:
                    ret_x = __extract__(v, k)
                else:
                    ret_x = __extract__(v, f"{key}.{k}")

                ret+= ret_x
    return ret


def get_all_keyword_fields(client: elasticsearch.Elasticsearch, index: str)->typing.Optional[typing.List[str]]:
    mapping = get_mapping(client, index)
    ret = __extract__(mapping)
    return ret
def get_meta_info_keyword_fields(client: elasticsearch.Elasticsearch, index: str)->typing.Optional[typing.List[str]]:
    data = get_all_keyword_fields(client, index)
    return [x[len("meta_info."):] for x in data if x.startswith("meta_info.")]

def make_meta_value(client: elasticsearch.Elasticsearch, index: str,field_list:typing.Optional[typing.List[str]]):
    if field_list is None:
        return
    properties={}
    for x in field_list:
        properties[f"meta_value.{x}"]={
            "fielddata": True,
            "type": "text"
        }
    client.indices.put_mapping(
        index=index,
        body={
            "properties": properties
        }
    )
