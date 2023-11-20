import typing

import elasticsearch
import elasticsearch.exceptions

FIELD_RAW_TEXT = "FIELDS_WILD_CARD_V2"


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


def get_all_keyword_fields(
        client: elasticsearch.Elasticsearch,
        index: str) -> typing.Optional[typing.List[str]]:
    mapping = get_mapping(client, index)
    ret = __extract__(mapping)

    return [x for x in ret if
            x != FIELD_RAW_TEXT or f".{FIELD_RAW_TEXT}." in x or "meta_info" == x or ".meta_info." in x]


def get_meta_info_keyword_fields(
        client: elasticsearch.Elasticsearch,
        index: str) -> typing.Optional[typing.List[str]]:
    data = get_all_keyword_fields(client, index)
    return [x[len(f"{FIELD_RAW_TEXT}."):] for x in data if
            x.startswith(f"{FIELD_RAW_TEXT}.") and not x.startswith("meta_info.")]


def __well_form_text__(content:typing.Optional[str])->typing.Optional[str]:
    if content is None:
        return None
    special_chracter=[
        "\n",
        "\r",
        "\t"
    ]
    for ch in special_chracter:
        if ch in content:
            content=content.replace(ch," ")
    while "  " in content:
        content = content.replace("  "," ")
    content = content.rstrip(" ").lstrip(" ")
    return content




def get_fields_text(
        data: typing.Optional[dict],
        key: typing.Optional[typing.List[str]] = None,
        ret_dict: typing.Optional[typing.Dict] = None,
        skip_fields: typing.Optional[typing.List[str]] = [
            "*_bm25_seg",
            "*_vn_predict",
            "meta_data",
            "meta_info",
            "privileges",
            "Privileges",
            FIELD_RAW_TEXT,
            "vn_non_accent_content",
            "*.data_item",
            "*_lower"
        ]
) -> typing.Tuple[typing.Optional[typing.List[str]], typing.Optional[typing.Dict]]:
    assert key is None or isinstance(key, list), "key must be none or list of text"
    if key is None:
        key = []
    if ret_dict is None:
        ret_dict = {}
    ret = []
    vals = ret_dict
    key_len = len(key)
    if data is None:
        return [], {}
    for k, v in data.items():
        is_skip = False
        key_check = k
        if key_len > 0:
            key_check = f"{'.'.join(key)}.{k}"
        for fx in skip_fields:
            if fx[0] == "*":
                is_skip = fx[1:] in key_check
                if is_skip:
                    break
            elif fx == key_check:
                is_skip = True
                if is_skip:
                    break
        if is_skip:
            continue

        if isinstance(v, str):
            well_form_value = __well_form_text__(v)
            if key_len == 0:
                ret += [k]
                vals[k] = well_form_value
            else:
                ret += [f"{'.'.join(key)}.{k}"]
                _f_vals_ = ret_dict
                _len_keys_ = len(key)
                for _k_ in range(0, _len_keys_):
                    if _f_vals_.get(key[_k_]) is None:
                        _f_vals_[key[_k_]] = {}
                    _f_vals_ = _f_vals_[key[_k_]]
                _f_vals_[k] = well_form_value
                # vals[f"{key}.{k}"] = v
        if isinstance(v, dict) and v != {}:
            key += [k]

            _ret_, _vals_ = get_fields_text(v, key, ret_dict)
            ret += _ret_
            vals = {**vals, **_vals_}
    return ret, vals


__cache_mapping__ = {}


def __create_mapping__(client: elasticsearch.Elasticsearch, index: str, fields: typing.List[str]):
    properties = {}
    for x in fields:
        properties[f"{FIELD_RAW_TEXT}.{x}"] = {
            # "fielddata": True,
            "type": "wildcard"
        }
    client.indices.put_mapping(
        index=index,
        body={
            "properties": properties
        }
    )


def update_mapping(
        client: elasticsearch.Elasticsearch,
        index: str,
        data: typing.Optional[dict]) -> typing.Tuple[typing.List[str], typing.Dict]:
    global __cache_mapping__
    if __cache_mapping__.get(index) is None:
        fields_from_mapping = get_all_keyword_fields(client, index) or []
        __create_mapping__(client=client, index=index, fields=fields_from_mapping)
        __cache_mapping__[index] = fields_from_mapping
    fields_from_data, values_from_data = get_fields_text(data)
    ret = list(set(fields_from_data).difference(set(__cache_mapping__[index])))
    if len(ret) > 0:

        properties = {}
        # FIELD_RAW_TEXT.data_item.meta_data.meta_info
        for x in ret:
            if ".meta_data.meta_data" in x or "data_item.meta_data." in x:
                continue
            properties[f"{FIELD_RAW_TEXT}.{x}"] = {
                # "fielddata": True,
                "type": "wildcard"
            }
        client.indices.put_mapping(
            index=index,
            body={
                "properties": properties
            }
        )
        __cache_mapping__[index] += ret
    return ret, values_from_data


def make_meta_value(client: elasticsearch.Elasticsearch, index: str):
    fields_list = get_all_keyword_fields(client, index)
    clone_fields = [x for x in fields_list or [] if not x.startswith("meta_data.")]

    if clone_fields is None:
        return
    properties = {}
    for x in clone_fields:
        properties[f"{FIELD_RAW_TEXT}.{x}"] = {
            "fielddata": True,
            "type": "text"
        }
    client.indices.put_mapping(
        index=index,
        body={
            "properties": properties
        }
    )


from cy_es.cy_es_docs import DocumentFields


def get_all_indexes(client: elasticsearch.Elasticsearch, prefix: str):
    indices = client.indices.get_alias().keys()
    ret = [x for x in indices if x.startswith(prefix)]
    return ret


filters = DocumentFields()


def get_docs(client: elasticsearch.Elasticsearch,
             index: str,
             fields: typing.Optional[typing.List[str]] = None,
             filter: typing.Optional[typing.Union[dict, DocumentFields]] = None,
             sort: typing.Optional[typing.List[dict]] = None,
             skip: typing.Optional[int] = 0,
             limit: typing.Optional[int] = 10) -> typing.Optional[typing.Iterator[dict]]:
    assert isinstance(client, elasticsearch.Elasticsearch), "client must be elasticsearch.Elasticsearch"
    _filter_ = filter or {}
    if isinstance(_filter_, DocumentFields):
        _filter_ = _filter_.__get_expr__()
    if isinstance(fields, list):
        _filter_["_source"] = [x for x in fields if isinstance(x, str)]
    _filter_["from"] = skip
    _filter_["size"] = limit
    if isinstance(sort, list):
        for x in sort:
            assert isinstance(x, dict)
            if x[list(x.keys())[0]] not in ["desc", "asc"]:
                raise Exception("sort must be something like [{\"create_on\":\"desc\"}]")
        _filter_["sort"] = sort
    ret = None
    try:
        ret = client.search(
            index=index,
            body=_filter_
        )
    except elasticsearch.exceptions.RequestError as e:
        if not hasattr(e, "info") and not isinstance(e.info, dict):
            raise e
        if not isinstance(e.info.get('error'), dict):
            raise e
        if not isinstance(e.info.get('error').get("root_cause"), list):
            raise e
        if len(e.info['error']['root_cause']) == 0:
            raise e
        if not isinstance(e.info['error']['root_cause'][0], dict):
            raise e
        if "maxClauseCount is set to " in e.info['error']['root_cause'][0]['reason']:
            items = e.info['error']['root_cause'][0]['reason'].split("is set to ")
            if (len(items) < 1):
                raise
            maxClauseCount = int(e.info['error']['root_cause'][0]['reason'].split("is set to ")[1])
            client.indices.update_settings(index=index, body={"maxClauseCount": maxClauseCount * 2})
            ret = client.search(
                index=index,
                body=_filter_
            )
        else:
            raise e

    ret_data = []
    total = 0
    if isinstance(ret.get("hits"), dict):
        if isinstance(ret["hits"].get("total"), dict):
            total = ret["hits"]["total"].get("value") or 0
        ret_data = ret["hits"].get("hits") or []

    def get_value():
        for x in ret_data:
            if x.get("_source"):
                ret_dict = x.get("_source")
                ret_dict["_id"] = x["_id"]
                yield ret_dict
            else:
                yield None

    return get_value(), total


def update_doc_by_id(
        client: elasticsearch.Elasticsearch,
        index: str, id: str,
        data: typing.Union[typing.Dict, typing.Tuple, DocumentFields],
        skip_update_mapping: typing.Optional[bool] = False
):
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
    if data_update.get("_id"):
        del data_update["_id"]
    if not skip_update_mapping:
        if data_update.get(FIELD_RAW_TEXT):
            data_update.pop(FIELD_RAW_TEXT)
        kes, values = update_mapping(client=client, index=index, data=data_update)
        data_update[FIELD_RAW_TEXT] = values
        # if isinstance(values.get("data_item"),dict) and isinstance(values.get("data_item").get("meta_data"),dict):
        #     print("loop")
        #     del values["data_item"]["meta_data"]
        # if isinstance(data_update[FIELD_RAW_TEXT].get("data_item"),dict):
        #     if data_update[FIELD_RAW_TEXT].get("data_item").get("meta_data"):
        #         data_update[FIELD_RAW_TEXT].get("data_item")["meta_data"]=None
        #         print("too long")
        # FIELD_RAW_TEXT.data_item.FIELD_RAW_TEXT
        # FIELD_RAW_TEXT.data_item.FIELD_RAW_TEXT
        try:
            data_update[FIELD_RAW_TEXT]['data_item'].pop(FIELD_RAW_TEXT)
            print("too long FIELD_RAW_TEXT.data_item.FIELD_RAW_TEXT")
        except:
            pass
        # if isinstance(data_update[FIELD_RAW_TEXT].get("data_item"),dict):
        #     if data_update[FIELD_RAW_TEXT].get("data_item").get(FIELD_RAW_TEXT):
        #         data_update[FIELD_RAW_TEXT].get("data_item")[FIELD_RAW_TEXT]=None
        #         print("too long")
        # FIELD_RAW_TEXT.data_item.meta_data.meta_data
        # FIELD_RAW_TEXT.data_item.meta_data.meta_data
        try:
            data_update[FIELD_RAW_TEXT]["data_item"].pop("meta_data")
            print("too long FIELD_RAW_TEXT.data_item.meta_data.meta_data")
        except:
            pass
        try:
            data_update[FIELD_RAW_TEXT]["data_item"].pop(FIELD_RAW_TEXT)
            print("too long FIELD_RAW_TEXT.data_item.FIELD_RAW_TEXT")
        except:
            pass
        # FIELD_RAW_TEXT.data_item.meta_data

    try:
        data_update[f"{FIELD_RAW_TEXT}_FIX"] = True
        ret_update = client.update(
            index=index,
            id=id,
            doc_type="_doc",
            body=dict(
                doc=data_update
            )

        )
        data_update["_id"] = id
        return ret_update, data_update
    except Exception as e:
        raise e


def get_doc(
        client: elasticsearch.Elasticsearch,
        index: str, id: str):
    ret = client.get(
        index=index,
        id=id,
        doc_type="_doc"
    )
    if isinstance(ret, dict) and isinstance(ret.get("_source"), dict):
        return ret["_source"]
    return None


def clean_up(data: typing.Optional[typing.Dict],
             fields: typing.Optional[typing.List[str]] = [
                 "*_bm25_seg",
                 "*_vn_predict",
                 "meta_data",
                 "FIELD_RAW_TEXT",
                 "FIELD_RAW_TEXT_V1",
                 "vn_non_accent_content",
                 "*.data_item",
                 "*_lower"
             ]):
    ret = {}
    if data is None:
        return None
    for k, v in data.items():
        is_clean = False
        for f in fields:
            if f[0] == "*":
                if k.endswith(f[1:]):
                    is_clean = True
                    break
            elif f == k:
                is_clean = True
                break
        if is_clean:
            ret[k] = None
        else:
            if isinstance(v,dict):
                ret[k] = clean_up(v)
            else:
                ret[k] = v

    return ret
