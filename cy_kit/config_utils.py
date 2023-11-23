import os
import typing


def flatten_dict(data: typing.Any) -> typing.Optional[
    typing.List[typing.Tuple[typing.AnyStr, typing.Any]]]:
    if data is None:
        return []
    ret = {}
    ret = []
    for k, v in data.items():
        if isinstance(v, dict):
            ret_list = flatten_dict(v)
            ret += [(f"{k}.{x}", y) for (x, y) in ret_list]
        else:
            ret += [(k, v)]
    return ret


def __get_key__(x: str):
    ret = ""
    len_of_x = len(x)
    i = 0
    while i < len_of_x:
        if x[i] == "_":
            if i < len_of_x:
                i = i + 1
                ret += x[i].upper()

            else:
                raise Exception(f"{x} is invalid config var. Config var looks like CONFIG_MY_VAR")
        else:
            if i==0:
                ret += x[i].upper()
            else:
                ret += x[i].lower()
        i=i+1
    return ret


def __get_dict__(k: str, v):
    items = [x for x in k.split(".")]
    tmp = {}
    ret = tmp
    len_of_items = len(items)
    for i in range(0, len_of_items - 1):
        key = items[i]
        if tmp.get(key) is None:
            tmp[key] = {}
        tmp = tmp[key]
    value = v
    if v.startswith("[") and v.endswith("]"):
        value = v[1:-1].split(",")
    tmp[items[len_of_items - 1]] = v
    return ret


def convert_env_to_dict(prefix: str = "config.") -> dict:
    ret = {}
    for k, v in os.environ.items():
        if k.startswith(f"{prefix}"):
            ret_dict = __get_dict__(k[len(prefix):], v)
            ret = {**ret, **ret_dict}
    return ret
