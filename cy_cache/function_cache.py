import types
import typing
from functools import cache
from memcache import Client
import hashlib
import json
import inspect
import cy_docs.cy_docs_x
__client__: Client = None
def __to_json_serilizable__(obj_value):
    ret = dict()
    if isinstance(obj_value,dict):
        for k,v in obj_value.items():
            ret[k] = __to_json_serilizable__(v)
        return ret
    elif hasattr(obj_value,"__dict__") and isinstance(obj_value.__dict__,dict):
        for k,v in obj_value.__dict__.items():
            ret[k] = __to_json_serilizable__(v)
        return ret
    elif obj_value is None:
        return None
    else:
        return str(obj_value)
@cache
def __get_key__(*args,**kwargs):
    hash_data = dict(
        args=args,
        kwargs=kwargs
    )
    txt_data = json.dumps(__to_json_serilizable__(hash_data))
    key = hashlib.sha256(txt_data.encode()).hexdigest()
    return key

def set_up(server: str):
    global __client__
    if __client__ is None:
        __client__ = Client(tuple(server.split(":")))


def caching( cache_time_in_minutes: int = 24):
    """
    This wrapper just use for get data from mongodb or read config. return value must be class object
    :param cache_time_in_minutes:
    :return:
    """
    if __client__ is None:
        raise Exception(f"It looks like you forgot set up memcache server. Please call {__file__}.setup")
    def wrapper(fn):
        assert callable(fn),"This wrapper just use for function"

        def run_fun(*args,**kwargs):
            master_key = __get_key__("v1/"+fn.__module__ + "/" + fn.__name__)
            # master_key_type = __get_key__("v1/"+fn.__module__ + "/" + fn.__name__+"/type")
            data= __client__.get(master_key) or {}
            args_key=__get_key__(json.dumps(dict(args=args,kwargs=kwargs)))

            if data.get(args_key) is None:

                ret_data = fn(*args,**kwargs)
                ret_type = None
                if ret_data is not None:
                    ret_type = type(ret_data)
                    if issubclass(ret_type,dict) and hasattr(ret_data,"to_json_convertable") and callable(ret_data.to_json_convertable):
                        ret_data = ret_data.to_json_convertable()
                cache_date = dict(
                    value = ret_data,
                    value_type = ret_type
                )
                __client__.set(master_key,cache_date)
            ret_dict = data[args_key]
            if ret_dict["value_type"]!=type(ret_dict["value"]) and issubclass(ret_dict["value_type"],dict):
                ret = ret_dict["value_type"](*ret_dict["value"])
                return ret
            else:
                return ret_dict["value"]

        return run_fun
    return wrapper
