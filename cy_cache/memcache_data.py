import typing
from functools import cache
from memcache import Client
import hashlib
import json
import inspect

__client__: Client = None


def set_up(server: str):
    global __client__
    if __client__ is None:
        __client__ = Client(tuple(server.split(":")))


@cache
def __get_key__(*args,**kwargs):
    hash_data = dict(
        args=args,
        kwargs=kwargs
    )
    txt_data = json.dumps(__to_json_serilizable__(hash_data))
    key = hashlib.sha256(txt_data.encode()).hexdigest()
    return key


def __is_full_keys__(keys, instance)->typing.Tuple[bool|None,str|None]:
    sub_key =dict()
    for k in keys:
        if not hasattr(instance,k) and getattr(instance,k) is None:
            return False, None
        else:
            sub_key[k] = __to_json_serilizable__(getattr(instance,k))
    json_key = json.dumps(sub_key)
    ret_key = hashlib.sha256(json_key.encode()).hexdigest()
    return True, ret_key


def __wrapper__init__(*args, **kwargs):
    global __client__
    __args__ = tuple(list(args)[1:])
    if __args__ == ():
        args[0].old_init(**kwargs)
    else:
        args[0].old_init(__args__, **kwargs)
    keys = type(args[0]).__manage_keys__
    hash_cache_key = type(args[0]).__hash_cache_key__
    cache_dict = __client__.get(hash_cache_key) or {}
    is_full,sub_key = __is_full_keys__(keys,args[0])
    if is_full:
        cache_dict[sub_key]=args[0]
        __client__.set(hash_cache_key,cache_dict)

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
def __wrapper__setattr__(self, key, value):
    global __client__
    keys = type(self).__manage_keys__
    hash_cache_key = type(self).__hash_cache_key__
    old_sub_dict= dict()
    master_dict = __client__.get(hash_cache_key) or {}
    for k in keys:
        val =__to_json_serilizable__(self.__dict__.get(k))
        old_sub_dict[k]=val

    old_key = hashlib.sha256(json.dumps(old_sub_dict).encode()).hexdigest()
    if master_dict.get(old_key):
        del master_dict[old_key]
    ret = self.__old_setattr__(key,value)
    new_sub_dict = dict()
    for k in keys:
        new_sub_dict[k]=__to_json_serilizable__(self.__dict__.get(k))
    new_key = hashlib.sha256(json.dumps(new_sub_dict).encode()).hexdigest()
    master_dict[new_key] = self
    __client__.set(hash_cache_key,master_dict)
    return ret

def __inspect_cache__(*args,**kwargs):
    instance = args[0]
    master_has_key =type(instance).__hash_cache_key__
    global __client__
    return __client__.get(master_has_key)
def __clear_cache__(*args,**kwargs):
    instance = args[0]
    master_has_key =type(instance).__hash_cache_key__
    global __client__
    return __client__.delete(master_has_key)
def __object__setattr__(*args,**kwargs):
    print("XX")
def cy_caching(keys=None):
    """
    Apply for class or function
    :param keys:
    :param server:
    :return:
    """
    def wrapper(*args, **kwargs):
        if isinstance(args[0], type):
            cls = args[0]
            if keys:
                if not hasattr(cls,"__annotations__"):
                    raise Exception(f"{cls} needs  annotations for declaring properties")
                for k in keys:
                    if not cls.__annotations__.get(k):
                        raise Exception(f"{k} was not found in {cls}")
            file_path = inspect.getfile(cls)+"/"+cls.__name__+".".join(keys)
            __hash_cache_key__ = __get_key__(file_path,None,None)
            setattr(cls, "__hash_cache_key__", __hash_cache_key__)
            setattr(cls, "__manage_keys__", keys or [])
            setattr(cls, "old_init", cls.__init__)
            setattr(cls, "__init__", __wrapper__init__)
            setattr(cls, "__old_setattr__", getattr(cls,"__setattr__"))
            setattr(cls,"__setattr__",__wrapper__setattr__)
            setattr(cls,"__inspect_cache__",__inspect_cache__)
            setattr(cls, "__clear_cache__", __clear_cache__)
            return cls
        elif isinstance(args[0], classmethod):
            cls_m: classmethod = args[0]

            def new_run_cls_mt(*f_args, **f_kwargs):
                global __client__
                file_path = inspect.getfile(cls_m.__func__)+"/"+cls_m.__func__.__name__
                key = __get_key__(
                    *tuple(list(f_args)[1:]+[file_path]),
                    **f_kwargs
                )
                ret = __client__.get(key)

                if ret is None:
                    ret_value = cls_m.__func__(*f_args, **f_kwargs)


                    ret = dict(ret_value=ret_value)
                    __client__.set(key, ret, time=4 * 3600)
                return ret["ret_value"]

            return new_run_cls_mt
        elif callable(args[0]):
            def new_run(*f_args, **f_kwargs):
                global __client__
                file_path = inspect.getfile(args[0])+"/"+args[0].__name__

                key = __get_key__(*tuple(list(args)[1:]+[file_path]), **f_kwargs )
                ret = __client__.get(key)

                if ret is None:
                    ret_value = args[0](*f_args, **f_kwargs)


                    ret = dict(ret_value=ret_value)
                    __client__.set(key, ret,time=4*3600)
                try:
                    setattr(ret["ret_value"], "__setattr__", __object__setattr__)
                except:
                    print(f"warning {type(ret['ret_value'])} can not track change")
                return ret["ret_value"]

            return new_run

    return wrapper
import typing
T=typing.TypeVar('T')

