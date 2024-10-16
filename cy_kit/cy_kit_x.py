"""
This library expose a concept was call cy_instance \n
TThư viện này đưa ra khái niệm cy_instance
cy_instance is an instance of Class which was generated by call on of below method: \n
cy_instance là một thể hiện của Lớp được tạo bằng cách gọi phương thức bên dưới \n
    provider, singleton, inject and scope \n
Actually, cy_instance does not create a instance of Class when call cy_kit.provider, cy_kit.singleton, cy_kit.inject or cy_kit.scope \n
Trên thực tế, cy_instance không instance của Lớp khi gọi cy_kit.provider, cy_kit.singleton, cy_kit.inject hoặc cy_kit.scope \n
The real instance of Class will create when thou access any property or method of Class \n
Phiên bản thực của Class sẽ tạo khi bạn truy cập bất kỳ thuộc tính hoặc phương thức nào của Class \n
Example:
    class MyClass:
      def hello():
        print('hello')

    ins = cy_kit.singleton(MyClass) # till now the instance of Class is not ready \n
                                    # cho đến bây giờ, Instance của Class vẫn chưa sẵn sàng
    ins.hello() # The instance of MyClass was created and call hello method
                # after this code the instance of Class will be held in memory and reuse for the next time
                Thể hiện của MyClass đã được tạo và gọi phương thức hello,
                thể hiện của Lớp sẽ được lưu trong bộ nhớ và sử dụng lại cho lần tiếp theo







"""

import json
import os.path
import threading
from typing import Iterable

import yaml
from copy import deepcopy

import logging

import inspect
import socket
from logging.handlers import RotatingFileHandler
from typing import List
import bson
import datetime
import ctypes
import signal
import sys


def __resolve_container__(cls: type):
    if not hasattr(cls, "__annotations__"):
        return inject(cls)
    ret = {}
    if cls.__annotations__.items().__len__() == 0:
        return inject(cls)
    for k, v in cls.__annotations__.items():
        if inspect.isclass(v):
            ret[k] = __resolve_container__(v)
        else:
            ret[k] = v
    return ret


def container(*args, **kwargs):
    def container_wrapper(cls):
        old_getattr = None
        if hasattr(cls, "__getattribute__"):
            old_getattr = getattr(cls, "__getattribute__")

        def __container__getattribute____(obj, item):
            ret = None
            if item[0:2] == "__" and item[:-2] == "__":
                if old_getattr is not None:
                    return old_getattr(obj, item)
                else:
                    ret = cls.__dict__.get(item)

            else:
                ret = cls.__dict__.get(item)
            if ret is None:
                __annotations__ = cls.__dict__.get('__annotations__')
                if isinstance(__annotations__, dict):
                    ret = __annotations__.get(item)

            if inspect.isclass(ret):

                ret_resolve = __resolve_container__(ret)
                if isinstance(ret_resolve, dict):
                    ret_instance = ret()
                    for k, v in ret_resolve.items():
                        setattr(ret_instance, k, v)
                    return ret_instance
                return ret

            return ret

        setattr(cls, "__getattribute__", __container__getattribute____)
        return cls()

    return container_wrapper


__cache_depen__ = {}
__lock_depen__ = threading.Lock()
__cache_yam_dict__ = {}
__cache_yam_dict_lock__ = threading.Lock()


def __change_init__(cls: type):
    """
    Re-modify the __init__ method of Class to call the base class __init__ method
    """
    if cls == object:
        return
    __old_init__ = cls.__init__

    def new_init(obj, *args, **kwargs):
        base = cls.__bases__[0]
        if base != object:
            base.__init__(obj, *args, **kwargs)
        __old_init__(obj, *args, **kwargs)

    setattr(cls, "__init__", new_init)


def resolve_singleton(cls, *args, **kwargs):
    """
    Create a instance of Class and hold it in memory for the next time and  make it singleton \n
    Tạo một thể hiện của Class và lưu nó trong bộ nhớ cho lần tiếp theo và đóng gói nó là singleton \n
    Example: \n
    """
    key = f"{cls.__module__}/{cls.__name__}"
    ret = None
    if __cache_depen__.get(key) is None:

        # __lock_depen__.acquire()
        try:

            n = len(cls.__bases__)
            for i in range(n - 1, 0):
                v = cls.__base__[i].__init__(v)
            __change_init__(cls)
            if hasattr(cls.__init__, "__defaults__"):
                if cls.__init__.__defaults__ is not None:
                    args = {}
                    for k, v in cls.__init__.__annotations__.items():
                        for x in cls.__init__.__defaults__:
                            if type(x) == v:
                                args[k] = x
                    v = cls(**args)
                else:
                    v = cls()
            else:
                v = cls()
            __cache_depen__[key] = v
        except Exception as e:
            raise e
        # finally:
        #     __lock_depen__.release()
    return __cache_depen__[key]


def resolve_scope(cls, *args, **kwargs):
    """
    Create scope of Class and hold it in memory for the next time and  make it singleton \n
    """
    if cls.__init__.__defaults__ is not None:
        args = {}
        for k, v in cls.__init__.__annotations__.items():
            for x in cls.__init__.__defaults__:
                if type(x) == v:
                    args[k] = x
        v = cls(**args)
    else:
        v = cls()
    return v


class VALUE_DICT(dict):
    """
    ValueDict is a class which hold a dictionary and provide a way to access to value by dot notation \n
    ValueDict là một lớp được tạo ra để lưu trữ một Từ điển và cung cấp cách truy cập giá trị bằng cách sử dụng dấu chấm \n
    Example: \n
    data = {a:1,b:{c:2,d:3}} \n
    data = ValueDict(data) \n
    print(data.a) // will print 1 \n
    print(data.b.c) // will print 2 \n
    print(data.b.d) // will print 3 \n
    print(data.b.e) // will raise AttributeError \n
    print(data.b.e.f) // will raise AttributeError \n
    print(data.b.e.f.g) // will raise AttributeError \n
    print(data.b.e.f.g.h) // will raise AttributeError \n
    print(data.b.e.f.g.h.i) // will raise AttributeError \n
    print(data.b.e.f.g.h.i.j) // will raise AttributeError \n
    """



    def __init__(self, data: dict):
        dict.__init__(self, **data)
        self.__data__ = data

    def __dir__(self) -> Iterable[str]:
        def get_property(d):
            ret = []
            if isinstance(d, dict):
                for k, v in d.items():
                    if isinstance(v, dict):
                        items = get_property(v)
                        for x in items:
                            ret += [f"{k}.{x}"]
                    else:
                        ret += [k]
            return ret

        return get_property(self.__data__)

    def __parse__(self, ret):
        if isinstance(ret, dict):
            return VALUE_DICT(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
        return ret

    def __get_errors__(self, attr: str):
        pors = dir(self)
        ret = f"{attr} was not found, available properties in in bellow list:\n"
        for x in pors:
            ret += f"\t{x}\n"
        return ret

    def __getattr__(self, item):
        if item[0:2] == "__" and item[-2:] == "__":
            return self.__dict__.get(item)
        if self.__data__.get(item) is None:
            raise AttributeError(self.__get_errors__(item))
        ret = self.__data__.get(item)
        if isinstance(ret, dict):
            return VALUE_DICT(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
            return ret_list
        return ret

    def to_dict(self):
        return self.__data__


def yaml_config(full_path_to_yaml_file: str, apply_sys_args: bool = True,env_prefix_config_key="config."):
    """
            Load yaml file , read content then parse to Dictionary.
        If thou set apply_sys_args is True.
        The arguments when thou start application will be applied to return Dictionary
            Tải tệp yaml, đọc nội dung rồi phân tích thành Từ điển.
        Nếu bạn đặt apply_sys_args là True.
        Các đối số khi bạn khởi động ứng dụng sẽ được áp dụng để trả về Từ điển
        Example: \n
            Yaml content is " my_value: value 1 " in file test.yml \n
            thou create python app looks like below: \n
                ret = yaml_config("test.yml", false) //will return {my_value:'value 1'} \n
                print(ret.my_value) \n
            and in command line exec: \n
            python my_app.py\n
            Thou will see value 1 \n
        The other case in command line exec:\n
            python my_app.py my_value='value 2' \n
            Thou will see value 2 \n
        ------------------------------------------------------------------------- \n

        Example: \n
            Yaml content is " my_value: value 1 "
            call yaml_config(..., false) will return {my_value:'value 1'}

        :param path:
        :param apply_sys_args:
        :return:
        """

    if not os.path.isfile(full_path_to_yaml_file):
        raise Exception(f"{full_path_to_yaml_file} was not found")
    if __cache_yam_dict__.get(full_path_to_yaml_file) is None:
        try:
            __cache_yam_dict_lock__.acquire()

            with open(full_path_to_yaml_file, 'r') as stream:
                __config__ = yaml.safe_load(stream)
                if apply_sys_args:
                    __config__ = combine_agruments(__config__)
                if env_prefix_config_key:
                    from cy_kit.config_utils import convert_env_to_dict
                    _config =convert_env_to_dict(env_prefix_config_key)
                    __config__ = {**__config__, **_config}
                __cache_yam_dict__[full_path_to_yaml_file] = VALUE_DICT(__config__)
        finally:
            __cache_yam_dict_lock__.release()

    return __cache_yam_dict__.get(full_path_to_yaml_file)


def convert_to_dict(str_path: str, value, ignore_cast=False):
    if not ignore_cast:
        if isinstance(value, str) and value[0:1] == "'" and value[:1] == "'":
            value = value[1:-1]
            ignore_cast = True
        elif isinstance(value, str) and value.lower() in ["true", "false"]:
            value = bool(value.lower() == 'true')
            ignore_cast = True
        elif isinstance(value, str) and "." in value:
            try:
                value = float(value)
                ignore_cast = True
            except Exception as e:
                value = value
                ignore_cast = True
        elif isinstance(value, str) and value.isnumeric():
            try:
                value = int(value)
                ignore_cast = True
            except Exception as e:
                value = value
                ignore_cast = True

    items = str_path.split('.')
    if items.__len__() == 1:
        return {items[0]: value}

    else:
        return {items[0]: convert_to_dict(str_path[items[0].__len__() + 1:], value, ignore_cast)}


def __dict_of_dicts_merge__(x, y):
    z = {}
    if isinstance(x, dict) and isinstance(y, dict):
        overlapping_keys = x.keys() & y.keys()
        for key in overlapping_keys:
            z[key] = __dict_of_dicts_merge__(x[key], y[key])
        for key in x.keys() - overlapping_keys:
            z[key] = deepcopy(x[key])
        for key in y.keys() - overlapping_keys:
            z[key] = deepcopy(y[key])
        return z
    else:
        return y


def combine_agruments(data):
    """
        Get all arguments when thou start python App and apply to data \n
        Example: \n
        ret = combine_agruments({a:1}) \n
        Will return {a:1} if thou start App without args \n
        And return {a:1,b:2} if thou start App with args is b=1
        ----------------------------------------------------------\n
        Nhận tất cả các đối số khi bạn khởi động Ứng dụng python và áp dụng cho dữ liệu \n
        Ví dụ: \n
        ret = Combine_agruments({a:1}) \n
        Sẽ trả về {a:1} nếu bạn khởi động Ứng dụng mà không có đối số \n
        Và trả về {a:1,b:2} nếu bạn khởi động Ứng dụng với args is b=1
    :param data:
    :return:
    """
    ret = {}
    for x in sys.argv:
        if x.split('=').__len__() == 2:
            k = x.split('=')[0]
            if x.split('=').__len__() == 2:
                v = x.split('=')[1]

                c = convert_to_dict(k, v)
                ret = __dict_of_dicts_merge__(ret, c)
            else:
                c = convert_to_dict(k, None)
                ret = __dict_of_dicts_merge__(ret, c)
    ret = __dict_of_dicts_merge__(data, ret)
    return ret


__provider_cache__ = dict()


def check_implement(interface: type, implement: type):
    global __config_provider_cache__
    global __provider_cache__

    if not inspect.isclass(implement):
        raise Exception(f"implement must be class")
    key = f"{interface.__module__}/{interface.__name__}/{implement.__module__}/{implement.__name__}"
    if __provider_cache__.get(key):
        return __provider_cache__[key]

    def get_module(cls):
        if not hasattr(cls, "__module__"):
            return None, None
        if not hasattr(cls, "__name__"):
            # raise Exception(f"{cls} don have __name__")
            return cls.__module__, None
        return cls.__module__, cls.__name__

    interface_methods = {}
    for x in interface.__bases__:
        for k, v in x.__dict__.items():
            if k[0:2] != "__" and k[:-2] != "__":
                handler = v
                if not inspect.isclass(handler) and callable(handler):
                    if isinstance(v, classmethod):
                        handler = v.__func__
                    interface_methods[k] = handler
    for k, v in interface.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__":
            handler = v
            if isinstance(v, classmethod):
                handler = v.__func__
            if not inspect.isclass(handler) and callable(handler):
                interface_methods[k] = handler
    implement_methods = {}

    for k, v in implement.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__":
            handler = v
            if isinstance(v, classmethod):
                handler = v.__func__
            if not inspect.isclass(handler) and callable(handler):
                implement_methods[k] = v
    interface_method_name_set = set(interface_methods.keys())
    implement_methods_name_set = set(implement_methods.keys())
    miss_name = interface_method_name_set.difference(implement_methods_name_set)
    if miss_name.__len__() > 0:
        importers = {}
        msg = ""
        for x in miss_name:
            fnc_declare = ""
            handler = interface_methods[x]
            agr_count = min(handler.__code__.co_argcount, handler.__code__.co_varnames.__len__())
            i = 0
            for a in handler.__code__.co_varnames:
                if i < agr_count:

                    m = handler.__annotations__.get(a)
                    if m:
                        u, v = get_module(m)
                        if u != int.__module__:
                            importers[u] = v

                        if v is None:
                            fnc_declare += f"{a}:{m},"
                        else:
                            fnc_declare += f"{a}:{m.__name__},"
                    else:
                        fnc_declare += f"{a},"
                i += 1
            if fnc_declare != "":
                fnc_declare = fnc_declare[:-1]

            full_fnc_decalre = f"def {x}({fnc_declare})"

            if handler.__annotations__.get("return"):
                u, v = get_module(handler.__annotations__.get("return"))
                if u != int.__module__:
                    importers[u] = v
                return_type = handler.__annotations__.get('return')
                if hasattr(return_type, "__name__"):
                    full_fnc_decalre += f"->{handler.__annotations__.get('return').__name__}:"

                else:
                    try:
                        full_fnc_decalre += f"->{str(handler.__annotations__.get('return'))}:"
                    except Exception as e:

                        full_fnc_decalre += f":"
            else:
                full_fnc_decalre += ":"
            if handler.__doc__ is not None:
                full_fnc_decalre += f'\n\t"""{handler.__doc__}\t"""'
            else:
                full_fnc_decalre += f'\n\t"""\n\tsomehow to implement thy source here ...\n\t"""'
            msg += f"\n{full_fnc_decalre}\n" \
                   f"\traise NotImplemented"
        for k, v in importers.items():
            if v is None:
                msg = f"\nimport {k}\n{msg}"
            else:
                msg = f"\nfrom {k} import {v}\n{msg}"
        description = f"\nIt looks likes thou forgot implement thy source code\n\tPlease open file:\n\t\t\t{inspect.getfile(implement)}\n\t\t Then goto \n\t\t\t class {implement.__name__} \n\t\tinsert bellow code\n--------------------------------------------\n"
        raise Exception(f"{description}{msg}\n-----------------------\ngood luck!")


def must_implement(interface: type):
    def warpper(cls):
        check_implement(interface, cls)
        return cls

    return warpper


__config_provider_cache__ = {}
__config_provider_cache_lock__ = threading.Lock()

import typing

import importlib


def load_class_from_module_with_class_name(class_in_module: str) -> type:
    items = class_in_module.split('.')
    class_name = items[len(items) - 1]
    module_name = class_in_module[:-len(class_name) - 1]
    _module_ = importlib.import_module(module_name)
    ret = getattr(_module_, class_name)
    if not isinstance(ret, type):
        raise Exception(f"{class_in_module} is not class")
    return ret


def config_provider(from_class: typing.Union[type, str], implement_class: typing.Union[type, str]):
    """
    config_provider will change any cy_instance with from_class to cy_instance with implement_class \n
    config_provider sẽ thay đổi bất kỳ cy_instance nào với from_class thành cy_instance với implement_class
    Example:
        class A:
            def hello(): print('hello m name A')

        clas B:
            def hello(): print('hello m name B')
        cy_kit.config_provider(
            from_class=A,
            implement_class = B)
        instance = cy_kit.singleton(A)
        instance.hello()
        will see 'hello m name B'
    So, if thou wanna to get real Type of Instance Class call
        cy_kit_x.get_runtime_type( instance)
    :param from_class:
    :param implement_class:
    :return:
    """
    _from_class = from_class
    _implement_class = implement_class
    if isinstance(from_class, str):
        _from_class = load_class_from_module_with_class_name(from_class)
    if isinstance(_implement_class, str):
        _implement_class = load_class_from_module_with_class_name(implement_class)
    global __config_provider_cache__
    global __config_provider_cache_lock__
    if _from_class == _implement_class:
        raise Exception(f"invalid config provider")
    key = f"{_from_class.__module__}/{_from_class.__name__}"
    if __config_provider_cache__.get(key) is not None:
        return
    with __config_provider_cache_lock__:
        check_implement(_from_class, _implement_class)
        __config_provider_cache__[key] = _implement_class


__lazy_cache__ = {}


def provider(cls):
    global __lazy_cache__
    global __config_provider_cache__
    key = f"{cls.__module__}.{cls.__name__}"
    if __lazy_cache__.get(key):
        return __lazy_cache__[key]

    class lazy_cls:
        def __init__(self, cls):
            self.__cls__ = cls
            self.__ins__ = None

        def __get_ins__(self):
            key = f"{self.__cls__.__module__}/{self.__cls__.__name__}"

            if __config_provider_cache__.get(key) is None:
                raise Exception(
                    f"Thous must call config_provider for {self.__cls__.__module__}.{self.__cls__.__name__}")

            if self.__ins__ is None:
                self.__ins__ = resolve_singleton(__config_provider_cache__[key])
            return self.__ins__

        def __getattr__(self, item):
            ins = self.__get_ins__()
            return getattr(ins, item)

    __lazy_cache__[key] = lazy_cls(cls)
    return __lazy_cache__[key]


__lazy_injector__ = {}


def inject(cls):
    global __lazy_injector__
    global __config_provider_cache__
    key = f"{cls.__module__}/{cls.__name__}"
    if __lazy_injector__.get(key):
        return __lazy_injector__[key]

    class lazy_cls:
        def __init__(self, cls):
            self.__cls__ = cls
            self.__ins__ = None

        def __get_ins__(self):
            if self.__ins__ is None:
                if __config_provider_cache__.get(key) is None:
                    self.__ins__ = resolve_singleton(self.__cls__)
                else:
                    self.__ins__ = resolve_singleton(__config_provider_cache__.get(key))
            return self.__ins__

        def __getattr__(self, item):
            ins = self.__get_ins__()
            return getattr(ins, item)

    __lazy_injector__[key] = lazy_cls(cls)
    return __lazy_injector__[key]


def scope(cls):
    global __config_provider_cache__
    key = f"{cls.__module__}/{cls.__name__}"

    class lazy_scope_cls:
        def __init__(self, cls):
            self.__cls__ = cls
            self.__ins__ = None

        def __get_ins__(self):
            if self.__ins__ is None:
                if __config_provider_cache__.get(key) is None:
                    self.__ins__ = resolve_scope(self.__cls__)
                else:
                    self.__ins__ = resolve_scope(__config_provider_cache__.get(key))
            return self.__ins__

        def __getattr__(self, item):
            ins = self.__get_ins__()
            return getattr(ins, item)

    __lazy_injector__[key] = lazy_scope_cls(cls)
    return __lazy_injector__[key]


def singleton(cls):
    global __lazy_injector__
    global __config_provider_cache__
    key = f"{cls.__module__}/{cls.__name__}"
    if __lazy_injector__.get(key):
        return __lazy_injector__[key]

    class lazy_cls:
        def __init__(self, cls):
            self.__cls__ = cls
            self.__ins__ = None

        def __get_ins__(self):
            if self.__ins__ is None:
                if __config_provider_cache__.get(key) is None:
                    self.__ins__ = resolve_singleton(self.__cls__)
                else:
                    self.__ins__ = resolve_singleton(__config_provider_cache__.get(key))
            return self.__ins__

        def __getattr__(self, item):
            ins = self.__get_ins__()
            return getattr(ins, item)

    __lazy_injector__[key] = lazy_cls(cls)
    return __lazy_injector__[key]


def thread_makeup():
    def wrapper(func):
        def runner(*args, **kwargs):
            class cls_run:
                def __init__(self, fn, *a, **b):
                    self.th = threading.Thread(target=fn, args=a, kwargs=b)

                def start(self):
                    self.th.start()
                    return self

                def join(self):
                    self.th.join()
                    return self

            return cls_run(func, *args, **kwargs)

        return runner

    return wrapper


def get_local_host_ip():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr


def create_logs(logs_dir, name: str) -> logging.Logger:
    full_dir = os.path.abspath(
        os.path.join(
            logs_dir, name
        )
    )
    if not os.path.isdir(full_dir):
        os.makedirs(full_dir, exist_ok=True)
    logger = logging.getLogger(name)
    handler = RotatingFileHandler(os.path.join(full_dir, f'{name}.log'), maxBytes=2000, backupCount=10)
    logger.addHandler(handler)

    _logs = logging.Logger("name")
    hdlr = RotatingFileHandler(
        full_dir + '/log.txt',
        maxBytes=1024 * 64,
        backupCount=200,
        encoding='utf8',

    )
    logFormatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s")
    hdlr.setFormatter(logFormatter)
    _logs.addHandler(hdlr)
    return _logs


def get_runtime_type(injector_instance):
    if hasattr(injector_instance, "__cls__"):
        cls = injector_instance.__cls__
        key = f"{cls.__module__}/{cls.__name__}"
        if __config_provider_cache__.get(key):
            return __config_provider_cache__[key]
        return injector_instance.__cls__
    else:
        return None


def singleton_from_path(injector_path: str):
    module_name, class_name = injector_path.split(':')

    if sys.modules.get(module_name) is None:
        raise ModuleNotFoundError(f"{module_name} was not found")
    if hasattr(sys.modules[module_name], class_name):
        cls_type = getattr(sys.modules[module_name], class_name)
        return singleton(cls_type)
    else:
        raise ModuleNotFoundError(f"{class_name} was not found in {module_name}")


def __to_json_convertable__(data):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = __to_json_convertable__(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [__to_json_convertable__(x)]
        return ret
    elif isinstance(data, bson.ObjectId):
        return data.__str__()
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    else:
        return data


def to_json(data) -> str:
    return json.dumps(__to_json_convertable__(data))


def clean_up():
    if sys.platform == "linux":
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)


class Graceful_Application(object):
    """
    Make an application instance with graceful exit
    """

    def __init__(self, on_run, on_stop):
        if sys.platform == "linux":
            self.shutdown = False
            # Registering the signals
            signal.signal(signal.SIGINT, self.__exit_graceful__)
            signal.signal(signal.SIGTERM, self.__exit_graceful__)

            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        self.on_run = on_run
        self.on_stop = on_stop

    def __exit_graceful__(self, signum, frame):
        self.shutdown = True
        print(f"app will stop {self.on_stop}")
        self.on_stop()
        sys.exit(0)

    # def __run__(self):
    #     time.sleep(1)
    #     print("running App: ")
    #
    # def __stop__(self):
    #     # clean up the resources
    #     print("stop the app")
    #     self.on_stop()
    def start(self):
        self.on_run()


def trip_content(data):
    """
        Remove any white space in left and right of data if data is text
        In the case of data is Dictionary.
        The method will detect all values in data and remove any white space in left and right
        -----------------------------------------------------------\n
        Xóa mọi khoảng trắng ở bên trái và bên phải của dữ liệu nếu dữ liệu là văn bản
        Trong trường hợp dữ liệu là Dictionary.
        Phương pháp này sẽ phát hiện tất cả các giá trị trong dữ liệu và xóa mọi khoảng trắng ở bên trái và bên phải
        :param data:
        :return:
    """

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.rstrip(' ').lstrip(' ')
            elif isinstance(v, dict):
                data[k] = trip_content(v)
    return data


import typing


def loop_process(loop_data: typing.Union[range, list, set, tuple]):
    import multiprocessing as mp
    from threading import Thread
    def __wrapper__(func: typing.Callable):

        def __start__(q: typing.List, x):
            ret = func(x)
            q.append(ret)

        def __run__(use_thread=True):
            if not use_thread:
                ret = []
                for row in loop_data:
                    ret += [func(row)]
                return ret

            ths = []
            q = []
            for row in loop_data:
                th = Thread(target=__start__, args=(q, row,))
                ths += [th]
                clean_up()

            for x in ths:
                x.start()
                clean_up()
            # for p in ths:
            #     ret = q.get()  # will block
            #     rets.append(ret)
            #     clean_up()
            for p in ths:
                p.join()
            clean_up()
            return q

        return __run__

    return __wrapper__


def sync_call():
    import asyncio
    def __wrapper__(func):
        def run(*args, **kwargs):
            asyncio.run(func(*args, **kwargs))
            clean_up()

        return run

    return __wrapper__


def watch_forever(sleep_time=0.0001):
    """
    This decoration will make up a function run in thread.
    The inner wrapper function must return a tuple of (Function, Function) in which:
        The first function in return values use for time checking. It looks like this:
            def check()->bool:
                return datetime.datetime.now().day()==2
        The second function in return values use for forever looping routine
            while True:
                if check():
                    ... The second function call here
    Full example:
        @cy_kit.watch_forever(sleep_time=1)
        def my_run(seconds: int):
            start_time = datetime.datetime.now()
            data = dict(count=0)
            print(f"Start at ={start_time}")
            print(f"This is the demonstrated how to print 'Hello!' in every 5 second")

            def check(data):
                return datetime.datetime.now().second % seconds == 0

            def run(data):
                global count
                count = data["count"]
                count+=1
                data["count"]=count
                print(f"Hello. This is {count} is say")

            return data, check, run


    :return:
    """
    import multiprocessing as mp
    import time
    def wraper(func):
        def run(*args, **kwargs):
            data, check, running = func(*args, **kwargs)
            while (True):
                if check(data):
                    th = threading.Thread(target=running, args=(data,))
                    th.start()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                clean_up()

        def start(*args, **kwargs):
            p = threading.Thread(target=run, args=args, kwargs=kwargs)
            p.start()
            p.join()
            clean_up()
            return p

        return start

    return wraper


def flatten_dict(data: typing.Optional[typing.Dict]) -> typing.Optional[
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
