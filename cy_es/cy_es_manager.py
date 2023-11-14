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
        if isinstance(k, str) and k.endswith("_bm25_seg"):
            continue
        if isinstance(k, str) and k.endswith("_bm25_bm25_seg"):
            continue
        if isinstance(k, str) and k.endswith("_bm25_seg_bm25_seg"):
            continue
        if isinstance(k, str) and k.endswith("_bm25_seg_vn_predict"):
            continue
        if isinstance(k, str) and k.endswith("_bm25_seg_vn_predict"):
            continue
        if isinstance(k, str) and k.endswith("_vn_predict"):
            continue
        if isinstance(v, dict):
            if isinstance(v.get("fields"), dict):
                if isinstance(v.get("fields").get("keyword"), dict):
                    if key:
                        ret += [f"{key}.{k}"]
                    else:
                        ret += [k]
                    continue
            if isinstance(v.get("properties"), dict):
                if key is None:
                    ret_x = __extract__(v, k)
                else:
                    ret_x = __extract__(v, f"{key}.{k}")

                ret += ret_x
    return ret


def get_all_keyword_fields(client: elasticsearch.Elasticsearch, index: str) -> typing.Optional[typing.List[str]]:
    mapping = get_mapping(client, index)
    ret = __extract__(mapping)
    return ret


def get_meta_info_keyword_fields(client: elasticsearch.Elasticsearch, index: str) -> typing.Optional[typing.List[str]]:
    data = get_all_keyword_fields(client, index)
    return [x[len("fields_value."):] for x in data if x.startswith("fields_value.") and not x.startswith("meta_info.")]


def get_fields_text(data: typing.Optional[dict], key: typing.Optional[str] = None) -> typing.Optional[typing.List[str]]:
    ret = []
    if data is None:
        return []
    for k, v in data.items():
        if isinstance(v, str):
            if key is None:
                ret += [k]
            else:
                ret += [f"{key}.{k}"]
        if isinstance(v, dict):
            ret += get_fields_text(v, k)
    return ret


__cache_mapping__ = {}


def __create_mapping__(client: elasticsearch.Elasticsearch, index: str, fields:typing.List[str]):
    properties = {}
    for x in fields:
        properties[f"fields_value.{x}"] = {
            "fielddata": True,
            "type": "text"
        }
    client.indices.put_mapping(
        index=index,
        body={
            "properties": properties
        }
    )



def update_mapping(client: elasticsearch.Elasticsearch, index: str, data: typing.Optional[dict]):
    global __cache_mapping__
    if __cache_mapping__.get(index) is None:
        fields_from_mapping = get_all_keyword_fields(client, index) or []
        __create_mapping__(client=client, index=index,fields= fields_from_mapping)
        __cache_mapping__[index] = fields_from_mapping
    fields_from_data = get_fields_text(data) or []
    ret = list(set(fields_from_data).difference(set(__cache_mapping__[index])))
    if len(ret) > 0:

        properties = {}
        for x in ret:
            properties[f"fields_value.{x}"] = {
                "fielddata": True,
                "type": "text"
            }
        client.indices.put_mapping(
            index=index,
            body={
                "properties": properties
            }
        )
        __cache_mapping__[index] += ret
    return ret
def make_meta_value(client: elasticsearch.Elasticsearch, index: str):
    fields_list = get_all_keyword_fields(client, index)
    clone_fields = [x for x in fields_list or [] if not x.startswith("meta_data.")]

    if clone_fields is None:
        return
    properties = {}
    for x in clone_fields:
        properties[f"fields_value.{x}"] = {
            "fielddata": True,
            "type": "text"
        }
    client.indices.put_mapping(
        index=index,
        body={
            "properties": properties
        }
    )
