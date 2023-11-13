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


def get_all_keyword_fields(client, index):
    mapping = get_mapping(client, index)
    ret = __extract__(mapping)
